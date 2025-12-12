import uvicorn
from app.config import get_settings
# from pyngrok import ngrok

settings = get_settings()
token = settings.ngrok_api
port = settings.port

# def start_ngrok():
#     ngrok.kill()
#     ngrok.set_auth_token(token)

#     try:
#         for tunnel in ngrok.get_tunnels():
#             ngrok.disconnect(tunnel.public_url)
#     except:
#         pass

#     http_tunnel = ngrok.connect(port)
#     print("Public URL:", http_tunnel.public_url)
#     return http_tunnel.public_url


# if __name__ == "__main__":
#     # Only parent process should run ngrok
#     if multiprocessing.current_process().name == "MainProcess":
#         public_url = start_ngrok()
#     else:
#         public_url = None

#     try:
#         uvicorn.run(
#             "app.main:app",
#             host="0.0.0.0",
#             port=port,
#             reload=settings.debug,
#             log_level=settings.log_level.lower(),
#         )
#     finally:
#         if public_url:
#             ngrok.disconnect(public_url)
#         ngrok.kill()

if __name__ == "__main__":
     uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=port,
            reload=settings.debug,
            log_level=settings.log_level.lower(),
        )