import firebase_admin
from firebase_admin import credentials, messaging

# ⿡ Inicializar Firebase con la clave del servicio
cred = credentials.Certificate("metroba-2335c-firebase-adminsdk-fbsvc-225a92a0f8.json")
firebase_admin.initialize_app(cred)

# ⿢ Función para enviar una notificación push a un topic
def enviar_notificacion_topic(topic, titulo, cuerpo, datos_extra=None):
    """
    Envía una notificación push a todos los dispositivos suscritos a un topic de FCM.
    
    :param topic: Nombre del topic (por ejemplo, 'lineaB', 'alertas', 'pruebas')
    :param titulo: Título de la notificación
    :param cuerpo: Cuerpo del mensaje
    :param datos_extra: Diccionario opcional con datos personalizados (línea, estación, tipo de alerta, etc.)
    """

    mensaje = messaging.Message(
        notification=messaging.Notification(
            title=titulo,
            body=cuerpo
        ),
        data=datos_extra if datos_extra else {},
        topic=topic
    )

    # ⿣ Enviar la notificación
    try:
        respuesta = messaging.send(mensaje)
        print(f"✅ Notificación enviada al topic '{topic}': {respuesta}")
    except Exception as e:
        print(f"❌ Error al enviar notificación al topic '{topic}': {e}")

# ⿤ Ejemplos de uso para el subte MetroBA
if _name_ == "_main_":
    # 🚧 Ejemplo 1: Interrupción del servicio en la Línea B
    enviar_notificacion_topic(
        topic="lineaB",
        titulo="⚠ Interrupción en la Línea B",
        cuerpo="Servicio interrumpido entre Medrano y Federico Lacroze.",
        datos_extra={
            "tipo": "alerta",
            "linea": "B",
            "estado": "interrumpido",
            "accion": "ver_detalles"
        }
    )

    # 🚇 Ejemplo 2: Próxima llegada de tren
    enviar_notificacion_topic(
        topic="lineaB",
        titulo="🚇 Tu tren llega en 2 minutos",
        cuerpo="El próximo tren hacia Catedral está por arribar a la estación Malabia.",
        datos_extra={
            "tipo": "tiempo_real",
            "linea": "B",
            "estacion": "Malabia",
            "direccion": "Catedral"
        }
    )

    # 🛠 Ejemplo 3: Mantenimiento programado en la Línea D
    enviar_notificacion_topic(
        topic="lineaD",
        titulo="🛠 Mantenimiento programado",
        cuerpo="La Línea D estará cerrada mañana de 22:00 a 5:00.",
        datos_extra={
            "tipo": "mantenimiento",
            "linea": "D",
            "fecha": "2025-10-27",
            "horario": "22:00-05:00"
        }
    )

    # 🧪 Ejemplo 4: Notificación general de prueba
    enviar_notificacion_topic(
        topic="pruebas",
        titulo="🚇 Prueba general de MetroBA",
        cuerpo="Esto es una notificación de prueba para todos los usuarios del topic 'pruebas'."
    )
