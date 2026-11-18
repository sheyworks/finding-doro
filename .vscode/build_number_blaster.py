import bpy
import math
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "number_blaster_fbx")
os.makedirs(OUT, exist_ok=True)

PALETTE = {
    "shell": (0.82, 0.90, 0.88, 1),
    "blue": (0.025, 0.48, 0.70, 1),
    "dark": (0.035, 0.075, 0.10, 1),
    "red": (0.82, 0.065, 0.10, 1),
    "yellow": (1.0, 0.66, 0.055, 1),
    "glow": (0.23, 0.92, 0.95, 1),
    "rubber": (0.12, 0.16, 0.18, 1),
}
MATS = {}

def material(key):
    if key in MATS:
        return MATS[key]
    rgba = PALETTE[key]
    mat = bpy.data.materials.new("M_Blaster_" + key)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.58
    if key == "glow":
        mat.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = rgba
        mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.35
    MATS[key] = mat
    return mat

def finish_obj(obj, key):
    obj.data.materials.append(material(key))
    return obj

def block(name, loc, size, key, bevel=0.035, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rotation:
        obj.rotation_euler = rotation
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    finish_obj(obj, key)
    if bevel:
        mod = obj.modifiers.new("Low poly softened edges", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj

def cylinder(name, loc, radius, depth, key, axis="Y", vertices=8):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    obj = bpy.context.object
    obj.name = name
    if axis == "Y":
        obj.rotation_euler[0] = math.pi/2
    elif axis == "X":
        obj.rotation_euler[1] = math.pi/2
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return finish_obj(obj, key)

# Receiver and broad toy-like shoulder stock.
block("Main receiver", (0, 0.02, 1.05), (0.48, 0.62, 0.38), "shell", 0.055)
block("Rear cap", (0, 0.34, 1.05), (0.52, 0.16, 0.42), "blue", 0.045)
block("Top rail", (0, 0.00, 1.28), (0.28, 0.40, 0.08), "dark", 0.018)
block("Top sight base", (0, -0.03, 1.36), (0.12, 0.10, 0.11), "yellow", 0.015)

# Short octagonal energy barrel points toward the front (-Y).
cylinder("Energy barrel", (0, -0.49, 1.08), 0.145, 0.82, "blue", "Y", 8)
cylinder("Muzzle collar", (0, -0.92, 1.08), 0.19, 0.15, "yellow", "Y", 8)
cylinder("Muzzle rim", (0, -1.015, 1.08), 0.15, 0.045, "dark", "Y", 8)
cylinder("Energy aperture", (0, -1.043, 1.08), 0.088, 0.012, "glow", "Y", 8)

# Grip, trigger and guard, kept chunky and easy to see at game scale.
block("Grip", (0, 0.13, 0.68), (0.15, 0.16, 0.34), "blue", 0.025,
      (math.radians(-8), 0, math.radians(-5)))
block("Grip panel", (0, 0.043, 0.68), (0.105, 0.025, 0.22), "rubber", 0.012,
      (math.radians(-8), 0, math.radians(-5)))
block("Trigger", (0, -0.20, 0.84), (0.055, 0.12, 0.18), "yellow", 0.012,
      (math.radians(-15),0,0))
block("Trigger guard lower", (0, -0.14, 0.74), (0.25, 0.055, 0.045), "dark", 0.012)
block("Trigger guard front", (0, -0.25, 0.80), (0.045, 0.055, 0.12), "dark", 0.012)

# Side-mounted number cell and simple energy status pips.
cylinder("Number cell", (0.30, 0.05, 1.08), 0.16, 0.14, "red", "X", 6)
block("Cell cap", (0.39, 0.05, 1.08), (0.045, 0.11, 0.22), "yellow", 0.015)
for i, key in enumerate(("glow", "yellow", "red")):
    block("Charge pip %d" % (i+1), (0.257, -0.015 + i*0.085, 1.34),
          (0.07, 0.055, 0.055), key, 0.012)

# Bold raised number on both sides of the receiver.
for side in (-1, 1):
    bpy.ops.object.text_add(location=(side*0.246, -0.095, 0.96), rotation=(math.pi/2, 0, 0))
    text = bpy.context.object
    text.name = "Number 3 marking"
    text.data.body = "3"
    text.data.align_x = "CENTER"
    text.data.align_y = "CENTER"
    text.data.size = 0.21
    text.data.extrude = 0.003
    # Text normal points outward from each side.
    if side < 0:
        text.rotation_euler[1] = math.pi
    bpy.ops.object.convert(target="MESH")
    finish_obj(bpy.context.object, "yellow")

# Join components into one compact prop mesh while preserving material slots.
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
bpy.ops.object.join()
weapon = bpy.context.object
weapon.name = "Handle"
# The object origin is the hand attachment point, centered in the grip.
bpy.context.scene.cursor.location = (0, 0.13, 0.68)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
bpy.ops.export_scene.fbx(
    filepath=os.path.join(OUT, "number_blaster.fbx"),
    use_selection=True,
    apply_unit_scale=True,
    bake_space_transform=True,
    object_types={"MESH"},
    add_leaf_bones=False,
    mesh_smooth_type="OFF",
    path_mode="AUTO",
    axis_forward="-Z",
    axis_up="Y",
)
triangles = sum(len(poly.vertices)-2 for poly in weapon.data.polygons)
print("Exported Number Blaster", triangles, "triangles")
