import bpy
import math
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "number_pistol_fbx")
os.makedirs(OUT, exist_ok=True)

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

COLORS = {
    "shell": (0.80, 0.88, 0.86, 1),
    "blue": (0.02, 0.42, 0.64, 1),
    "dark": (0.025, 0.055, 0.075, 1),
    "rubber": (0.095, 0.13, 0.15, 1),
    "red": (0.78, 0.035, 0.065, 1),
    "yellow": (1.0, 0.60, 0.035, 1),
    "glow": (0.12, 0.82, 0.91, 1),
}
MATERIALS = {}

def mat(key):
    if key in MATERIALS:
        return MATERIALS[key]
    rgba = COLORS[key]
    material = bpy.data.materials.new("M_Pistol_" + key)
    material.diffuse_color = rgba
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = 0.62
    if key == "glow":
        bsdf.inputs["Emission Color"].default_value = rgba
        bsdf.inputs["Emission Strength"].default_value = 0.35
    MATERIALS[key] = material
    return material

def block(name, loc, dims, material, bevel=0.025, rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if rotation:
        obj.rotation_euler = rotation
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    obj.data.materials.append(mat(material))
    if bevel:
        mod = obj.modifiers.new("Single segment bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj

def cylinder(name, loc, radius, depth, material, axis="Y", sides=8):
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides, radius=radius, depth=depth, location=loc)
    obj = bpy.context.object
    obj.name = name
    if axis == "Y":
        obj.rotation_euler[0] = math.pi/2
    elif axis == "X":
        obj.rotation_euler[1] = math.pi/2
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.data.materials.append(mat(material))
    return obj

# Pistol upper frame and slide, with the muzzle facing forward (-Y).
block("Lower frame", (0, 0.015, 1.015), (0.38, 0.50, 0.20), "blue", 0.035)
block("Slide", (0, -0.015, 1.175), (0.42, 0.57, 0.20), "shell", 0.035)
block("Slide top rail", (0, -0.02, 1.285), (0.20, 0.38, 0.04), "dark", 0.01)

# Compact octagonal barrel and recessed dark muzzle.
cylinder("Barrel", (0, -0.415, 1.175), 0.105, 0.56, "dark", "Y", 8)
cylinder("Muzzle ring", (0, -0.705, 1.175), 0.135, 0.09, "yellow", "Y", 8)
cylinder("Bore", (0, -0.755, 1.175), 0.082, 0.012, "dark", "Y", 8)
cylinder("Energy core", (0, -0.765, 1.175), 0.042, 0.014, "glow", "Y", 8)

# Low front and rear sights.
block("Front sight", (0, -0.58, 1.305), (0.07, 0.075, 0.055), "yellow", 0.01)
block("Rear sight L", (-0.12, 0.205, 1.305), (0.055, 0.07, 0.075), "dark", 0.01)
block("Rear sight R", (0.12, 0.205, 1.305), (0.055, 0.07, 0.075), "dark", 0.01)

# Angled grip sized for a chunky character hand. Its center is the export pivot.
grip_rot = (math.radians(-18), 0, 0)
block("Pistol grip", (0, 0.17, 0.755), (0.18, 0.22, 0.43), "rubber", 0.03, grip_rot)
block("Grip side plate", (0.096, 0.17, 0.755), (0.025, 0.15, 0.30), "blue", 0.012, grip_rot)
block("Grip heel", (0, 0.225, 0.525), (0.205, 0.22, 0.065), "yellow", 0.015,
      (math.radians(-12), 0, 0))
for i in range(3):
    block("Grip rib %d" % i, (0, 0.045, 0.655+i*0.075), (0.185, 0.025, 0.018), "dark", 0.005, grip_rot)

# Guard and trigger sit in the natural space ahead of the grip.
block("Trigger guard lower", (0, -0.145, 0.885), (0.235, 0.055, 0.045), "dark", 0.012)
block("Trigger guard front", (0, -0.255, 0.935), (0.05, 0.055, 0.13), "dark", 0.012)
block("Trigger", (0, -0.205, 0.975), (0.045, 0.10, 0.11), "yellow", 0.01,
      (math.radians(-18), 0, 0))

# Small numbered power cell on both sides, without widening the gripping area.
cylinder("Power cell", (0.22, 0.02, 1.04), 0.105, 0.09, "red", "X", 6)
block("Power cell window", (0.272, 0.02, 1.04), (0.018, 0.09, 0.10), "glow", 0.008)
block("Three charge bars", (0.218, -0.02, 1.34), (0.08, 0.045, 0.035), "yellow", 0.008)

# Number emblem embossed on the visible left side of the slide.
bpy.ops.object.text_add(location=(-0.218, -0.105, 1.115), rotation=(math.pi/2, 0, -math.pi/2))
emblem = bpy.context.object
emblem.name = "Number 3 emblem"
emblem.data.body = "3"
emblem.data.align_x = "CENTER"
emblem.data.align_y = "CENTER"
emblem.data.size = 0.13
emblem.data.extrude = 0.002
bpy.ops.object.convert(target="MESH")
bpy.context.object.data.materials.append(mat("yellow"))

# Join to one static mesh named Handle; preserve the hand-grip as the local origin.
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
bpy.ops.object.join()
weapon = bpy.context.object
weapon.name = "Handle"
bpy.context.scene.cursor.location = (0, 0.17, 0.755)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

path = os.path.join(OUT, "number_pistol.fbx")
bpy.ops.export_scene.fbx(
    filepath=path,
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
print("Exported Number Pistol", triangles, "triangles")
