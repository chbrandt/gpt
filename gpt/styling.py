import logging as log

import xml.etree.ElementTree as ET


def fix_qml_style_on_field_name_change(qml: str, old_field_name: str, new_field_name: str) -> str:
    tree = ET.fromstring(qml)
    renderer = tree.find("renderer-v2")

    styletype = renderer.attrib["type"]
    if styletype == "categorizedSymbol":
        log.debug("Updating categorized symbols style")
        if renderer.attrib["attr"] == old_field_name:  # the field was used in this style
            renderer.attrib["attr"] = new_field_name

        else:  # nothing to do - not affected
            # log.debug("the field were not used as filter for the style")
            log.debug("the field were not used as filter for the style")
            return qml

    elif styletype == "RuleRenderer":
        log.debug("Updating rule-based symbols style")
        rules = renderer.find("rules").findall("rule")

        for rule in rules:
            filter_def = rule.attrib["filter"]
            log.debug(f"checking filter definition {filter_def}")
            usedfield = filter_def.split("=")[0].strip()
            if usedfield == old_field_name:
                log.debug(f"need to update filter {filter_def}")
                new_filter = new_field_name + " " + filter_def[filter_def.index("="):]
                rule.attrib["filter"] = new_filter
                log.info(f"updating filter def {filter_def} to {new_filter}")

            else:
                log.debug("the field were not used as filter for the style")
                return qml

    else:
        log.warning(f"Style type {styletype} is not supported (yet)")
        return qml

    newstyle = str(ET.tostring(tree, encoding='unicode', method='xml'))
    return newstyle


def fix_sld_style_on_field_name_change(sld: str, old_field_name: str, new_field_name: str) -> str:
    import xml.etree.ElementTree as ET
    tree = ET.fromstring(sld)
    prefix_map = {"ogc": "http://www.opengis.net/ogc"} # we should read this from the xml itself
    propertynames = list(tree.findall(".//ogc:PropertyName", prefix_map))
    for prop in propertynames:
        if prop.text == old_field_name:
            log.debug(f"modifying field in sld from {prop.text} to {new_field_name}")
            prop.text = new_field_name

    newstyle = str(ET.tostring(tree, encoding='unicode', method='xml'))
    return newstyle


def ensure_just_one_default_style(styles, layer_name):
    """perform some checks on the style table and clean if possible"""
    ids = list(styles.loc[styles["f_table_name"] == layer_name].index) # ids of the possible style for this layer
    defaults = list(styles.loc[ ids, "useAsDefault"]) # the default flag for these rows

    if len(ids) == 0:
        #log.error("no style for this layer found")
        print("no style for this layer found")
        return

    if len(ids) == 1:
        id = ids[0] # use that as style

    else: # we select the first style that is also set as default
        try:
            first_default  = defaults.index(True)
            id = ids[first_default]
        except: # no style set as default
            #log.warning("No styles with default flag. using as style the last inserted. may be a problem!")
            print("No styles with default flag. using as style the last inserted. may be a problem!")
            id = ids[-1] # chose the last inserted

    styles.loc[ids, "useAsDefault"] = False # clear default flags, just to be sure, we may actually want to delete those unused styles
    styles.loc[id, "useAsDefault"] = True # now set the default style