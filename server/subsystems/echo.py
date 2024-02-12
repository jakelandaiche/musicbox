from ..subsystem import Subsystem

echo = Subsystem("Echoer")
@echo.all
async def echo_message(message, _):
    print("Received message")
    print(message)

