from flask import Flask, render_template, request, redirect, url_for
import os
from utils import calculate_similarity

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.secret_key = 'code-clone-secret'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Home page to upload files."""
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare():
    """Handle file uploads and perform code clone detection."""
    file1 = request.files['file1']
    file2 = request.files['file2']

    if file1 and file2:
        file1_path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        file2_path = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)
        file1.save(file1_path)
        file2.save(file2_path)

        # Perform similarity analysis
        result = calculate_similarity(file1_path, file2_path)
        feedback = generate_feedback(result["string_similarity"], result["token_similarity"])

        return render_template('result.html',
                               file1=file1.filename,
                               file2=file2.filename,
                               result=result,
                               feedback=feedback)
    return redirect(url_for('index'))

def generate_feedback(string_similarity, token_similarity):
    """Generate feedback based on similarity scores."""
    if string_similarity > 0.8 or token_similarity > 0.8:
        return "The codes are very similar. Consider refactoring to avoid duplication."
    elif string_similarity > 0.5 or token_similarity > 0.5:
        return "The codes have moderate similarity. Review and refactor if necessary."
    else:
        return "The codes are sufficiently different."

if __name__ == '__main__':
    app.run(debug=True)
