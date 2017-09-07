from OpenSSL import SSL
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('priv.key')
context.use_certificate_file('pub.crt')