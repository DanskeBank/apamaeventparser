

class ApamaEvent(object):
    def __init__(self, channel='', package_name='', event_name='', fields=None):
        if not fields:
            fields = []
        self.channel = channel
        self.package_name = package_name
        self.event_name = event_name
        self.fields = fields

    def __unicode__(self):
        p = self.package_name + '.' if self.package_name else ''
        c = '"' + self.channel + '",' if self.channel else ''
        f = ', '.join([str(field) for field in self.fields])
        return '%s%s%s(%s)' % (c, p, self.event_name, f)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)
