import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional
import sys

@dataclass
class Position:
    x: float
    y: float
    z: float

    @staticmethod
    def from_elem(elem: ET.Element) -> "Position":
        return Position(
            x=float(elem.get("x", 0.0)),
            y=float(elem.get("y", 0.0)),
            z=float(elem.get("z", 0.0))
        )

@dataclass
class HomePosition:
    position: Position
    tolerance: float

@dataclass
class Condition:
    type: str
    result: str
    value: Optional[float] = None
    position: Optional[Position] = None
    tolerance: Optional[float] = None
    max_velocity: Optional[float] = None

@dataclass
class EndConditions:
    conditions: List[Condition]

@dataclass
class HUDText:
    start_message: str
    success_message: str
    failure_message: str

@dataclass
class BackgroundColor:
    r: float
    g: float
    b: float

@dataclass
class Camera:
    position: Position
    look_at: Position
    up: Position

@dataclass
class SceneSettings:
    background_color: BackgroundColor
    camera: Camera

@dataclass
class ObjectConfig:
    id: str
    type: str
    position: Position
    orientation: Position
    size: dict
    color: Optional[BackgroundColor] = None
    file: Optional[str] = None
    scale: Optional[Position] = None

@dataclass
class TrialConfig:
    home: HomePosition
    end_conditions: EndConditions
    hud_text: HUDText
    scene_settings: SceneSettings
    objects: List[ObjectConfig]


def xml_parser(xml_path: str) -> TrialConfig:
    tree = ET.parse(xml_path)
    root = tree.getroot()

# HomePosition
    home_elem = root.find("HomePosition")
    pos_elem = home_elem.find("Position")
    tol_elem = home_elem.find("Tolerance")
    home = HomePosition(
        position  = Position.from_elem(pos_elem),
        tolerance = float(tol_elem.text)
    )

    # EndConditions
    conds = []
    for c in root.find("EndConditions").findall("Condition"):
        cond = Condition(
            type = c.get("type"),
            result = c.get("result"),
            value = float(c.get("value")) if c.get("value") else None
        )
        if c.find("Position") is not None:
            cond.position  = Position.from_elem(c.find("Position"))
        if c.find("Tolerance") is not None:
            cond.tolerance = float(c.findtext("Tolerance"))
        if c.find("MaxVelocity") is not None:
            cond.max_velocity = float(c.findtext("MaxVelocity"))
        conds.append(cond)
    end_conditions = EndConditions(conditions=conds)

    # HUDText
    hud = root.find("HUDText")
    hud_text = HUDText(
        start_message   = hud.findtext("StartMessage"),
        success_message = hud.findtext("SuccessMessage"),
        failure_message = hud.findtext("FailureMessage")
    )

    # SceneSettings
    ss = root.find("SceneSettings")
    bg = ss.find("BackgroundColor")
    background_color = BackgroundColor(
        r=float(bg.get("r")),
        g=float(bg.get("g")),
        b=float(bg.get("b"))
    )
    cam = ss.find("Camera")
    camera = Camera(
        position = Position.from_elem(cam.find("Position")),
        look_at = Position.from_elem(cam.find("LookAt")),
        up = Position.from_elem(cam.find("Up"))
    )
    scene_settings = SceneSettings(
        background_color=background_color,
        camera=camera
    )

    # Objects
    objs = []
    for obj in root.find("Objects").findall("Object"):
        position    = Position.from_elem(obj.find("Position"))
        orientation = Position.from_elem(obj.find("Orientation"))

        size_elem = obj.find("Size")
        if size_elem is not None:
            size = {k: float(v) for k, v in size_elem.attrib.items()}
        else:
           size = {}

        color_elem = obj.find("Color")
        color = (
            BackgroundColor(
                r=float(color_elem.get("r")),
                g=float(color_elem.get("g")),
                b=float(color_elem.get("b"))
            )
            if color_elem is not None
            else None
        )

        file = obj.findtext("File")

        scale_elem = obj.find("Scale")
        if scale_elem is not None:
            scale = Position.from_elem(scale_elem) 
        else:
            scale = None

        objs.append(ObjectConfig(
            id          = obj.get("id"),
            type        = obj.get("type"),
            position    = position,
            orientation = orientation,
            size        = size,
            color       = color,
            file        = file,
            scale       = scale
        ))

    return TrialConfig(
        home           = home,
        end_conditions = end_conditions,
        hud_text       = hud_text,
        scene_settings = scene_settings,
        objects        = objs
    )


if __name__ == "__main__":
    cfg = xml_parser(sys.argv[1])

    print("Home Position:", cfg.home.position, "±", cfg.home.tolerance)
    print("\nEnd Conditions:")
    for c in cfg.end_conditions.conditions:
        print(f" - {c.type} → {c.result}", end="")
        if c.value:         print(f", value={c.value}", end="")
        if c.position:      print(f", at {c.position}", end="")
        if c.tolerance:     print(f", tol={c.tolerance}", end="")
        if c.max_velocity:  print(f", max_vel={c.max_velocity}", end="")
        print()

    print("\nHUD Messages:")
    print(" Start:",   cfg.hud_text.start_message)
    print(" Success:", cfg.hud_text.success_message)
    print(" Failure:", cfg.hud_text.failure_message)

    print("\nScene Settings:")
    print(" Background color:", cfg.scene_settings.background_color)
    print(" Camera pos:",       cfg.scene_settings.camera.position)
    print(" Camera look-at:",   cfg.scene_settings.camera.look_at)
    print(" Camera up:",        cfg.scene_settings.camera.up)

    print("\nObjects:")
    for obj in cfg.objects:
        print(f" • [{obj.type}] {obj.id}")
        print("    Position:",    obj.position)
        print("    Orientation:", obj.orientation)
        print("    Size:",        obj.size)
        if obj.color:    print("    Color:", obj.color)
        if obj.file:     print("    File:",  obj.file)
        if obj.scale:    print("    Scale:", obj.scale)