"""Convert OBJ + MTL + textures to embedded GLB using trimesh.

Usage:
  python scripts/obj_to_glb.py assets/models/logo_cube.obj assets/models/logo_cube.glb

If trimesh is not installed, the script will print instructions to install it
or to use Blender for conversion.
"""
import sys
import os

try:
    import trimesh
    from trimesh.exchange import gltf
except Exception:
    trimesh = None


def convert(obj_path, glb_path):
    if trimesh is None:
        print('trimesh not installed. Install with: pip install trimesh pyglet pygltflib')
        print('Alternatively, use Blender: blender --background --python convert_blender.py -- obj out.glb')
        return 2

    # load mesh, which should pick up material and textures
    mesh = trimesh.load(obj_path, force='mesh')
    if mesh is None:
        print('Failed to load OBJ:', obj_path)
        return 1

    # export to glb
    data = trimesh.exchange.gltf.export_glb(mesh)
    with open(glb_path, 'wb') as f:
        f.write(data)
    print('Wrote', glb_path)
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: obj_to_glb.py input.obj output.glb')
        sys.exit(1)
    sys.exit(convert(sys.argv[1], sys.argv[2]))
