# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import requests
import json
import os
from dotenv import load_dotenv
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
# URL del endpoint de la API
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={}".format(GOOGLE_API_KEY)
# Cabeceras para la petición
headers = {
    'Content-Type': 'application/json',
}
# Datos (payload) para enviar en la petición POST
data = {
    "contents": [{
        "role":"user",
        "parts": [{
            "text": ""
        }]
    }]
}

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler para el lanzamiento de la skill."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        data["contents"][0]["parts"][0]["text"] = "Serás mi asistente de I.A. Te daré comandos y vamos a interactuar según te oriente y entrene."
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            text = (response_data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "Texto no encontrado"))
            speak_output = text + " ¿En qué puedo ayudarte?"
            response_text = {
                "role": "model",
                "parts": [{
                    "text": text
                }]
            }
            data["contents"].append(response_text)
        else:
            speak_output = "Error en la solicitud."
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class ChatIntentHandler(AbstractRequestHandler):
    """Handler para el intent de chat."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ChatIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        query = handler_input.request_envelope.request.intent.slots["query"].value
        query_text = {
                "role": "user",
                "parts": [{
                    "text": query
                }]
            }
        data["contents"].append(query_text)
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            text = (response_data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "Texto no encontrado"))
            speak_output = text
            response_text = {
                "role": "model",
                "parts": [{
                    "text": text
                }]
            }
            data["contents"].append(response_text)
        else:
            speak_output = "No obtuve una respuesta para tu solicitud."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("¿Tienes otra pregunta?")
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Handler para Cancelar y Detener."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "¡Hasta luego!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Manejo genérico de errores para capturar cualquier error de sintaxis o de enrutamiento."""
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Lo siento, tuve problemas para procesar tu solicitud. Por favor, intenta de nuevo."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# El objeto SkillBuilder actúa como punto de entrada para tu skill, enruta todas las peticiones y respuestas
# a los handlers definidos arriba. Asegúrate de incluir cualquier nuevo handler o interceptor aquí.
# El orden importa: se procesan de arriba hacia abajo.

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ChatIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
