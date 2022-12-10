import argparse
import os
import stat

import flask
from flask import jsonify
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint

"""This module implements a simple file access REST API."""

app = flask.Flask(__name__)


def dir_path(path):
    """Return path if it is a valid directory, ArgumentTypeError otherwise."""
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid directory path")


def parse_args():
    """Returns the parsed command line arguments, error if the arguments are invalid."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=dir_path, dest="root", metavar="DIR",
                        required=True, help="root directory for app")
    return parser.parse_args()


@app.route('/', methods=['GET'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET'])
def all_routes(path):
    """
    Process file and directory requests.
    Process file and directory requests.  Returns either a directory listing or the file contents.
    ---
    produces:
    - application/json
    - text/plain
    definitions:
      - schema:
          id: FileEntry
          properties:
            name:
                type: string
                description: the file entry name
            owner:
                type: integer
                description: the file entry owner ID
            permissions:
                type: string
                description: the octal file entry permissions
            size:
                type: integer
                description: The file entry size in bytes
            isDir:
                type: boolean
                description: Whether the file entry is a directory or not
            isFile:
                type: boolean
                description: Whether the file entry is a regular file or not
    parameters:
        - in: path
          name: path
          description: The optional directory or file path to display. Cannot contain .. parent directory.
          required: false
          type: string
    responses:
        200:
            description: Directory listing or file contents returned.
            schema:
                type: array
                items:
                    $ref: /api/spec#/definitions/FileEntry
            examples:
                application/json:
                    name: myfile
                    owner: 501
                    permissions: 755
                    size: 236
                    isDir: false
                    isFile: true
        400:
            description: Entry at path must be a regular file or directory and must not contain .. parent directory.
        404:
            description: Could not find entry at path.
    """
    # see if it's a file or directory
    try:
        full_path = args.root
        # Only join if the path is non-empty.
        if path:
            # Detect .. parent links in the input data to ensure that malicious
            # users can't access files outside the configured root path.
            if '..' in path:
                return f"Path {path} cannot contain the .. parent directory", 400
            full_path = os.path.join(args.root, path)

        entry_status = os.stat(full_path)
        mode = entry_status.st_mode
        if stat.S_ISDIR(mode):
            # If it's a directory, include all files in directory responses,
            # including hidden files. Include file name, owner, size, and
            # permissions (read/write/execute - standard octal
            # representation).
            entries = os.scandir(full_path)
            result = []
            for entry in entries:
                entry_data = {}

                entry_data["name"] = entry.name
                # These are not required, but are nice to have for the client.
                entry_data["isDir"] = entry.is_dir()
                entry_data["isFile"] = entry.is_file()

                entry_status = entry.stat()
                # Extract and format the octal permissions from the mode
                entry_data["permissions"] = oct(stat.S_IMODE(entry_status.st_mode))[-3:]
                entry_data["owner"] = entry_status.st_uid
                entry_data["size"] = entry_status.st_size

                # To make a HATEOAS app, include links to the child entries here.
                result.append(entry_data)

            return jsonify(result)

        elif stat.S_ISREG(mode):
            # If it's a file, return the text contents.
            # This assumes the files are a reasonable size and can be returned
            # via a simple response.
            with open(full_path) as f:
                # Note that this can't decode non-text files, but that's not
                # a requirement.
                return f.read()

        else:
            # File type that we do not handle (i.e. block special device file).
            return f"Entry at path {path} must be a regular file or directory", 400
    except FileNotFoundError:
        return f"Could not find entry at path {path}", 404


@app.route("/api/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "File Browser REST API"
    # Remove the duplicate path element from the routing to clean up the docs.
    del swag['paths']['/']
    return jsonify(swag)


swaggerui_blueprint = get_swaggerui_blueprint(
    '/api/docs',
    '/api/spec',
    config={
        'app_name': "File Browser REST API"
    }
)

app.register_blueprint(swaggerui_blueprint)

if __name__ == '__main__':
    args = parse_args()
    app.run(host="0.0.0.0", port=9007)
