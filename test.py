from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/run_command')
def run_command():
    command = ['echo', 'Hello, World!']  # replace with your command
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, error = process.communicate()

    if error:
        return f"An error occurred while trying to run the command: {error}"
    else:
        return f"The command was run successfully. Output: {output.decode('utf-8')}"

if __name__ == "__main__":
    app.run(debug=True)
