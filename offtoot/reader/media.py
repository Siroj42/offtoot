from offtoot.store.media import Media, get_media_type_name

def display_media(m: Media):
    disp = "(media type: {}) {}".format(get_media_type_name(m.media_type), m.description)
    print(disp)
    print("File: file://{}".format(m.get_path()))
