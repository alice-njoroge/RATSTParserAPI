from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api, reqparse, abort # to build RESTful API 
import to_sql  # metaprogramming module 

import parser 

app = Flask(__name__) # declaration this file (Inverted control )
api = Api(app) #give the api


class Index(Resource):
    """
    The index class
    it takes the relational query from the query fragment and parses it to python callable string 
    which is in return passed over to sql 
    """

    def get(self):
        """
        Get the query passed result
        :return:
        """
        req_parser = reqparse.RequestParser() #get the request 
        req_parser.add_argument('query', type=str, help='The relational query is required', required=True)
        args = req_parser.parse_args() # extract the query and convert the string to python dict marshling
        query = args.get('query') # get the query from the dictionary 
        try: # try catch errors 
            parsed_expression = parser.parse(query)
            sql_expression = to_sql.to_mysql(parsed_expression)
            return {'result': sql_expression}
        except (parser.ParserException, parser.TokenizerException) as e:
            return make_response((jsonify({'error': 'Sorry an error occurred, Try again.', 'error_message': str(e)})),
                                 400)
        


api.add_resource(Index, '/') # add url

if __name__ == '__main__': # run 
    app.run(debug=True)
