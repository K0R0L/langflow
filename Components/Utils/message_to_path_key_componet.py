from langflow.custom import Component
from langflow.io import MessageInput, Output
from langflow.schema import Data
from langflow.schema.message import Message
from loguru import logger


class ParsePathKeyComponent(Component):
    display_name = "ParsePathKey"
    description = "Split message to path and key."
    icon = "message-square-share"
    name = "MessagetoData"

    inputs = [
        MessageInput(
            name="message",
            display_name="Message",
            info="The Message object to convert to a Data object",
        ),
    ]

    outputs = [
        Output(display_name="Directory", name="directory", method="get_directory"),
        Output(display_name="Key", name="key", method="get_key"),
        Output(display_name="Output_key", name="output_key", method="get_output_key"),
    ]

    def get_directory(self) -> Message:
        if isinstance(self.message, Message):
            directory = str(self.message.text).split(",")[0].split(":")[1]
            return Message(text=directory)

        msg = "Error converting Message to Data: Input must be a Message object"
        logger.opt(exception=True).debug(msg)
        self.status = msg
        return Data(data={"error": msg})

    def get_key(self) -> Data:
        if isinstance(self.message, Message):
            directory = str(self.message.text).split(",")[1].split(":")[1]

            return Data(
                data={
                    "key_1": directory.split(";")[0],
                    "key_2": directory.split(";")[1],
                }
            )

        msg = "Error converting Message to Data: Input must be a Message object"
        logger.opt(exception=True).debug(msg)
        self.status = msg
        return Data(data={"error": msg})

    def get_output_key(self) -> Data:
        if isinstance(self.message, Message):
            directory = str(self.message.text).split(",")[1].split(":")[1]
            output_keys = directory.split(";")
            return Data(data={"output_keys": output_keys})

        msg = "Error converting Message to Data: Input must be a Message object"
        logger.opt(exception=True).debug(msg)
        self.status = msg
        return Data(data={"error": msg})
