import json

import SudoMagic


class ToxExporter:
    def __init__(self, ownerOp) -> None:
        self.inventory = SudoMagic.entities.githubCollection()
        self.inventory.author = ipar.Settings.Author.eval()
        self.inventory.source = ipar.Settings.Repo.eval()

        self.Release_dir_root: str = "../release/"
        self.Log_file: str = "log.txt"

        print("TOX Exporter Init")

    def Build_inventory(self) -> None:
        self._build_inventory()

    def Build_for_release(self) -> None:
        self._write_action_to_log("Starting Build process in TD")
        # build inventory
        self._build_inventory(log_to_file=True)

        # exit project
        project.quit(force=True)

    def _build_inventory(self, log_to_file: bool = False) -> None:
        print('-> Starting build process')

        name_to_type_map: dict[str, str] = {
            'base_templates': 'template',
            'base_sm_comps': 'tdComp'
        }

        op_sources: list[str] = ['base_tools']
        source_exclude_list: list[str] = ['base_template', 'base_icon']
        set_exclude_list: list[str] = ['base_icon',]

        for each_source in op_sources:
            blocks: list = op(each_source).findChildren(type=baseCOMP, depth=1)

            # handle all blocks / folders of examples
            for each_block in blocks:
                single_examples: list = each_block.findChildren(
                    type=baseCOMP, depth=1)

                # skip template and icon ops
                if each_block.name in source_exclude_list:
                    pass
                else:
                    print(f'--> {each_block.name}')
                    path: str = each_block.par.Blockname.eval()
                    info: dict = self._generate_op_info(
                        each_block, path)
                    self.inventory.collection.append(info)

                    # handle each example itself
                    for each_example in single_examples:
                        # skip template and icon ops
                        if each_example.name in source_exclude_list:
                            pass
                        else:

                            print(f'---> {each_example.name}')
                            self._write_action_to_log(
                                f'processing | {each_example.name}')
                            path: str = f"{each_block.par.Blockname.eval()}/{each_example.par.Compname.eval()}"
                            info: dict = self._generate_op_info(
                                each_example, path)
                            self.inventory.collection.append(info)

        print('-> completing build')
        self.write_inventory_to_file(self.inventory.to_dict())

    def _generate_op_info(self, target_op, path: str) -> dict:

        remote_op: SudoMagic.entities.remoteTox = SudoMagic.entities.remoteTox()
        # generate all the info needed for dict
        remote_op.asset_path
        remote_op.path = path
        remote_op.type_tag = SudoMagic.entities.cloudPaletteTypes.folder if 'block' in target_op.tags else SudoMagic.entities.cloudPaletteTypes.tdComp
        remote_op.display_name = target_op.par.Blockname.eval(
        ) if 'block' in target_op.tags else target_op.par.Compname.eval()
        remote_op.tox_version = "" if 'block' in target_op.tags else target_op.par.Toxversion.eval()
        remote_op.last_updated = "" if 'block' in target_op.tags else target_op.par.Lastsaved.eval()
        remote_op.td_version = "" if 'block' in target_op.tags else f'{target_op.par.Tdversion.eval()}.{target_op.par.Tdbuild.eval()}'
        remote_op.opFamilies = []
        remote_op.opTypes = []

        # write op to disk and generate path
        if 'block' in target_op.tags:
            remote_op.summary = target_op.par.Summarycontents.eval().text
        else:
            children_ops = target_op.findChildren()
            remote_op.asset_path = self.save_external(target_op)
            remote_op.opFamilies = list(
                set([each_op.family for each_op in children_ops]))
            remote_op.opTypes = list(
                set([each_op.OPType for each_op in children_ops]))

        return remote_op.to_dict()

    def _write_action_to_log(self, message: str) -> None:
        with open(self.Log_file, 'a+') as logFile:
            logFile.write(f"{message}\n")

    def write_inventory_to_file(self, inventory: dict) -> None:

        print('--> writing inventory to file')
        with open(f'{self.Release_dir_root}inventory.json', 'w+') as file:
            file.write(json.dumps(inventory))

    def save_external(self, target_op) -> str:
        asset_path = f'{target_op.id}.{target_op.name}.tox'
        save_path = f'{self.Release_dir_root}{asset_path}'
        target_op.save(save_path)
        return asset_path
