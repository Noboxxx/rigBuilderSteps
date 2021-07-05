import rigBuilder
from maya import cmds, mel
import os


@rigBuilder.log
def new_scene():
    cmds.file(new=True, force=True)


@rigBuilder.log
def import_maya_file(path):
    try:
        cmds.file(path, i=True)
    except RuntimeError as e:
        print(e)


@rigBuilder.log
def delete_useless_nodes():
    # Delete unknown nodes
    unknown_nodes = cmds.ls(type='unknown') or list()
    cmds.delete(unknown_nodes)

    # Delete unused nodes
    mel.eval('MLdeleteUnused;')


@rigBuilder.log
def transfer_skin(source, targets):
    def get_skinned_joints(mesh):
        joints_ = list()
        skin_clusters = [n for n in cmds.listHistory(mesh) or list() if cmds.objectType(n, isAType='skinCluster')]
        for skin_cluster in skin_clusters:
            joints_ += cmds.skinCluster(skin_cluster, query=True, inf=True) or list()
        joints_ = list(set(joints_))
        joints_.sort()
        return joints_

    def get_skin_cluster(mesh):
        for node_ in cmds.listHistory(mesh) or list():
            if cmds.objectType(node_, isAType='skinCluster'):
                return node_
        return None

    attributes = (
        'skinningMethod', 'useComponents', 'deformUserNormals', 'dqsSupportNonRigid',
        'dqsScaleX', 'dqsScaleY', 'dqsScaleZ', 'normalizeWeights', 'weightDistribution',
        'maintainMaxInfluences', 'maxInfluences', 'envelope'
    )

    parent_skin_cluster = get_skin_cluster(source)

    data = list()
    for attr in attributes:
        data.append((attr, cmds.getAttr('{0}.{1}'.format(parent_skin_cluster, attr))))

    joints = get_skinned_joints(source)
    for target in targets:
        # Wipe out any previous skinCluster on dest mesh
        if True in [cmds.objectType(node, isAType='skinCluster') for node in cmds.listHistory(target) or list()]:
            cmds.skinCluster(target, e=True, unbind=True)

        # Skin dest mesh with joints' meshes
        new_skin_cluster, = cmds.skinCluster(target, joints)

        for attr, value in data:
            cmds.setAttr('{0}.{1}'.format(new_skin_cluster, attr), value)

        # Transfer the skin
        cmds.copySkinWeights(source, target, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation=('name', 'closestJoint'))


@rigBuilder.log
def build_mgear(guide_path):
    import mgear.shifter.io
    mgear.shifter.io.build_from_file(filePath=guide_path)


@rigBuilder.log
def import_ctrls_shapes(path):
    import ctrlShaper
    if ctrlShaper.NurbsCurvesFile.is_one(path):
        ctrlShaper.NurbsCurvesFile(path).load()
    else:
        cmds.warning('\'{0}\' is not a valid.'.format(path))


@rigBuilder.log
def import_ng_skin_layers(path, target):
    import ngSkinTools2.api.transfer

    if os.path.isfile(path):
        layers_transfer = ngSkinTools2.api.transfer.LayersTransfer()
        layers_transfer.vertex_transfer_mode = ngSkinTools2.api.transfer.VertexTransferMode.vertexId
        layers_transfer.target = target
        layers_transfer.load_source_from_file(path)
        layers_transfer.execute()
    else:
        print('\'{}\' is not a valid path.'.format(path))


@rigBuilder.log
def create_asset_folder(meshes, components, asset_folder_name='asset', rig_folder_name='rig', geo_folder_name='geo'):
    rig_grp = cmds.group(name=rig_folder_name, empty=True)
    for component in components:
        cmds.parent(component, rig_grp)

    geo_grp = cmds.group(name=geo_folder_name, empty=True)
    for mesh in meshes:
        cmds.parent(mesh, geo_grp)

    asset_grp = cmds.group(name=asset_folder_name, empty=True)
    cmds.parent(geo_grp, rig_grp, asset_grp)
