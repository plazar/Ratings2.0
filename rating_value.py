class RatingValue(object):
    def __init__(self, name, version, description, value):
        self.name = name
        self.version = version
        self.description = description
        self.value = value

    def __str__(self):
        text  = "Rating name (version): %s (v%d)\n" % (self.name, self.version)
        text += "Description: %s\n" % self.description
        text += "Value: %.12g" % self.value
        return text 
