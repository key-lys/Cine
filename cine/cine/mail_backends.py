import ssl
from django.core.mail.backends.smtp import EmailBackend


class DevSMTPBackend(EmailBackend):
   """
   SMTP “dev” que fuerza STARTTLS sin verificar certificado.
   SOLO para desarrollo local.
   """
   def open(self):
       # si ya abrimos la conexión, salimos
       if self.connection:
           return False


       # abrimos conexión simple (deja que SMTPBackend maneje hostname interno)
       self.connection = self.connection_class(
           self.host,
           self.port,
       )


       # forzamos TLS SIN verificar certificado
       ctx = ssl._create_unverified_context()
       self.connection.starttls(context=ctx)


       # si tenemos credenciales, nos logueamos
       if self.username and self.password:
           self.connection.login(self.username, self.password)


       return True


