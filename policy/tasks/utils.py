def render_obj(attrs=[]):
    def inner(objname):
        return dict(filter(lambda x: x[0] in attrs,
                           objname.__dict__.iteritems()))
    return inner


render_vol_attachment = render_obj(
    attrs = [
        'device',
        'id',
        'serverId',
        'volumeId',
    ]
)

render_volume = render_obj(
    attrs = [
        'description',
        'id',
        'imageRef',
        'instance',
        'metadata',
        'name',
        'project_id',
        'size',
        'user_id',
        'volume_type',
        'os-vol-tenant-attr:tenant_id',
        'status'
    ]
)
