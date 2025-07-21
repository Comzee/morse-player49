from flask import Flask, request, jsonify
import csv
import os

app = Flask(__name__)

# Dictionary to store morse code mappings
morse_to_ascii = {}

def load_morse_mappings():
    """Load morse code mappings from ConfigMap CSV file"""
    config_path = '/etc/config/morse-code.csv'
    
    # For local testing, use a local file if ConfigMap doesn't exist
    if not os.path.exists(config_path):
        config_path = 'morse-code.csv'
    
    try:
        with open(config_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    ascii_char = row[0]
                    morse_code = row[1]
                    morse_to_ascii[morse_code] = ascii_char
        print(f"Loaded {len(morse_to_ascii)} morse code mappings")
    except Exception as e:
        print(f"Error loading morse mappings: {e}")

def decode_morse(morse_message):
    """Decode a morse code message to ASCII text"""
    decoded_message = ""
    
    # Split by '/' to get words
    words = morse_message.split('/')
    
    for word in words:
        if word.strip():  # Skip empty words
            # Split by spaces to get individual letters
            letters = word.strip().split(' ')
            for letter in letters:
                if letter in morse_to_ascii:
                    decoded_message += morse_to_ascii[letter]
                else:
                    # If we can't decode a character, add a placeholder
                    decoded_message += '?'
            decoded_message += ' '
    
    return decoded_message.strip()

@app.route('/decode-morse', methods=['POST'])
def decode_morse_endpoint():
    """API endpoint to decode morse code messages"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message in request body'}), 400
        
        morse_message = data['message']
        decoded_message = decode_morse(morse_message)
        
        # Print the decoded message as required
        print(f"Decoded message: {decoded_message}")
        
        # Check if the message contains a flag pattern
        # Common flag patterns include FLAG{...}, CTF{...}, or similar
        response = {
            'decoded': decoded_message,
            'original': morse_message
        }
        
        # Check for flag patterns
        flag_indicators = ['FLAG', 'CTF', 'KEY', 'CODE']
        for indicator in flag_indicators:
            if indicator in decoded_message.upper():
                response['flag_found'] = True
                print(f"Potential flag found: {decoded_message}")
                break
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error decoding morse: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Load morse mappings on startup
    load_morse_mappings()
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)