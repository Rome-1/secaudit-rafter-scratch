import grpc
from contextlib import contextmanager
from datetime import datetime

# Assuming appropriate imports from Flipt, such as token creation methods and auth metadata setups...

@contextmanager
def create_channel(server_address):
    channel = grpc.insecure_channel(server_address)
    try:
        yield channel
    finally:
        channel.close()


def test_audit_logging():
    server_address = 'localhost:9000'  # Assuming this is the address

    with create_channel(server_address) as channel:
        # Assuming the auth_stub and necessary request objects are available and properly configured
        # Example pseudocode for creating authentication
        create_request = auth.CreateAuthenticationRequest(
            Id='test_token_id',
            Metadata={'key': 'value'},
            Method=auth.Method.METHOD_TOKEN
        )

        auth_stub = auth.AuthenticationServiceStub(channel)
        
        # Create Authentication
        response = auth_stub.CreateAuthentication(create_request)
        
        print(f"Created Authentication: {response.Id}")


        # Test delete functionality (similar pattern)
        delete_request = auth.DeleteAuthenticationRequest(Id='test_token_id')
        auth_stub.DeleteAuthentication(delete_request)
        
        print(f"Deleted Authentication: {delete_request.Id}")


if __name__ == '__main__':
    test_audit_logging()
