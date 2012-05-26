import httplib
import json
import base64
import urllib

class UnknownGithubObject( Exception ):
    pass

class Requester:
    def __init__( self, login_or_token, password ):
        if password is not None:
            login = login_or_token
            self.__authorizationHeader = "Basic " + base64.b64encode( login + ":" + password ).replace( '\n', '' )
        elif login_or_token is not None:
            token = login_or_token
            self.__authorizationHeader = "token " + token
        else:
            self.__authorizationHeader = None
        self.rate_limiting = ( 5000, 5000 )

    def request( self, verb, url, parameters, input ):
        assert verb in [ "HEAD", "GET", "POST", "PATCH", "PUT", "DELETE" ]
        assert url.startswith( "https://api.github.com" )
        url = url[ len( "https://api.github.com" ) : ]

        headers = dict()
        if self.__authorizationHeader is not None:
            headers[ "Authorization" ] = self.__authorizationHeader

        cnx = httplib.HTTPSConnection( "api.github.com", strict = True )
        cnx.request(
            verb,
            self.__completeUrl( url, parameters ),
            json.dumps( input ),
            headers
        )
        response = cnx.getresponse()

        status = response.status
        headers = dict( response.getheaders() )
        output = self.__structuredFromJson( response.read() )

        cnx.close()

        self.rate_limiting = ( int( headers[ "x-ratelimit-remaining" ] ), int( headers[ "x-ratelimit-limit" ] ) )

        # print verb, url, parameters, input, "==>", status, str( headers )[ :30 ], str( output )[ :30 ]
        return status, headers, output

    def __completeUrl( self, url, parameters ):
        if parameters is None or len( parameters ) == 0:
            return url
        else:
            return url + "?" + urllib.urlencode( parameters )

    def __structuredFromJson( self, data ):
        if len( data ) == 0:
            return None
        else:
            return json.loads( data )
