import rigBuilder
from maya import cmds
import os


@rigBuilder.clock
def build_mgear(guide_path):
    print(guide_path)

    import mgear.shifter.io
    mgear.shifter.io.build_from_file(filePath=guide_path)


@rigBuilder.clock
def import_ctrls_shapes(path):
    print(path)

    import ctrlShaper
    if ctrlShaper.NurbsCurvesFile.is_one(path):
        ctrlShaper.NurbsCurvesFile(path).load()
    else:
        cmds.warning('\'{0}\' is not a valid.'.format(path))


@rigBuilder.clock
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
