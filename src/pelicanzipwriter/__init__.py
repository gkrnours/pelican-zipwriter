def add_writer(pelican_object):
    from pelicanzipwriter.writer import ZipWriter
    return ZipWriter

def register():
    from pelican import signals
    signals.get_writer.connect(add_writer)
    monkey_patch()

def monkey_patch():
    from pelican import generators
    def generate_output(self, writer):
        print("ook! ook")
    generators.StaticGenerator.generate_output = generate_output
