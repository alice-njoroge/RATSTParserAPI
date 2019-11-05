from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api, reqparse, abort
from werkzeug.exceptions import BadRequest
import to_sql

import parser

app = Flask(__name__)
api = Api(app)


class Index(Resource):
    """
    The index class
    """

    def get(self):
        """
        Get the query passed result
        :return:
        """
        req_parser = reqparse.RequestParser()
        req_parser.add_argument('query', type=str, help='The relational query is required', required=True)
        args = req_parser.parse_args()
        query = args.get('query')
        try:
            parsed_expression = parser.parse(query)
            sql_expression = to_sql.to_mysql(parsed_expression)
        except (parser.ParserException, parser.TokenizerException) as e:
            return make_response((jsonify({'error': 'Sorry an error occurred, Try again.', 'error_message': str(e)})),
                                 400)
        return {'result': sql_expression}


api.add_resource(Index, '/')

if __name__ == '__main__':
    app.run(debug=True)
