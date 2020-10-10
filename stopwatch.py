import time

import obspython as obs

scene_name = ""
source_name = ""
timer = False
start = 0
reset = True
scene_match = False
# ------------------------------------------------------------


def timed(sec):
    mins = sec // 60
    sec = sec % 60
    hours = mins // 60
    mins = mins % 60

    return "{:02d}:{:02d}:{:02d}".format(hours, mins, sec)


def stopwatch():
    global source_name
    global timer

    source = obs.obs_get_source_by_name(source_name)
    diff = time.time() - start
    if stop_stream and diff >= stop_stream_time:
        timer = False
        if obs.obs_frontend_streaming_active():
            obs.obs_frontend_streaming_stop()
            print('Stopwatch - Stream stopped!')
        if obs.obs_frontend_recording_active():
            obs.obs_frontend_recording_stop()
            print('Stopwatch - Recording stopped!')
        obs.timer_remove(stopwatch)
        obs.remove_current_callback()
    text = str(timed(int(diff)))
    try:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", text)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
    except UnboundLocalError:
        pass


def scene_updater():
    global scene_match
    global source_name

    global timer
    global start

    current_scene = obs.obs_source_get_name(obs.obs_frontend_get_current_scene())
    source = obs.obs_get_source_by_name(source_name)
    if source is not None and scene_name is not None:
        if scene_name == current_scene and scene_match is False:
            scene_match = True
            if timer == False:
                timer = True
                start = time.time()
                obs.timer_add(stopwatch, 200)
        elif scene_name != current_scene:
            scene_match = False
            if reset_time:
                timer = False
                obs.timer_remove(stopwatch)
    obs.obs_source_release(source)


def refresh_pressed(props, prop):
    scene_updater()


def reset_stopwatch_pressed(props, prop):
    global start
    start = time.time()
    obs.timer_remove(stopwatch)
    obs.timer_add(stopwatch, 200)
# ------------------------------------------------------------


def script_description():
    return "Stopwatch\nUpdates a Text source with a stopwatch like timer based on if the matching Scene is viewable.\n\n(Script can stop stream after set time as well.)\n\nBy Garulf"


def script_update(settings):
    global scene_name
    global source_name
    global reset_time
    global stop_stream
    global stop_stream_time

    scene_name = obs.obs_data_get_string(settings, "scene")
    source_name = obs.obs_data_get_string(settings, "source")
    reset_time = obs.obs_data_get_bool(settings, "reset_time")
    stop_stream = obs.obs_data_get_bool(settings, "stop_stream")
    stop_stream_time = obs.obs_data_get_int(settings, "stop_stream_time")
    obs.timer_remove(scene_updater)

    if scene_name != "" and source_name != "":
        obs.timer_add(scene_updater, 1000)


def script_unload():
    obs.timer_remove(stopwatch)
    obs.timer_remove(scene_updater)


def script_defaults(settings):
    obs.obs_data_set_bool(settings, "reset_time", True)
    obs.obs_data_set_bool(settings, "stop_stream", False)


def script_properties():
    props = obs.obs_properties_create()

    s = obs.obs_properties_add_list(props, "scene", "Scene",
                                    obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    p = obs.obs_properties_add_list(props, "source", "Text Source",
                                    obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)

    obs.obs_properties_add_bool(props, "reset_time", "Reset time on scene switch")

    obs.obs_properties_add_int(props, "stop_stream_time",
                               "Stop stream/record after (seconds):", 10, 7200, 1)
    obs.obs_properties_add_bool(props, "stop_stream", "Enabled")
    sources = obs.obs_enum_sources()

    if sources is not None:

        for source in sources:
            name = obs.obs_source_get_name(source)
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus" or source_id == "text_ft2_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)

        obs.source_list_release(sources)

    scenes = obs.obs_frontend_get_scenes()
    if scenes is not None:
        for scene in scenes:
            name = obs.obs_source_get_name(scene)
            obs.obs_property_list_add_string(s, name, name)

        obs.source_list_release(scenes)

    obs.obs_properties_add_button(props, "reset_button", "Reset Stopwatch", reset_stopwatch_pressed)
    obs.obs_properties_add_button(props, "button", "Refresh", refresh_pressed)
    return props
