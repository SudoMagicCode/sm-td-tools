import json


class ToxExporter:
    def __init__(self, ownerOp: callable) -> None:

        self.base_uri: str = "https://sudo-tools-td-templates.sudo.codes/builds/"
        self.release_dir_root: str = "../release/"

        print("TOX Exporter Init")

    def Build_inventory(self) -> None:
        self._build_inventory()

    def _build_inventory(self) -> None:
        print('-> Starting build process')

        inventory: dict = {
            "setup": {
                "base_uri": self.base_uri
            },
        }

        name_to_type_map: dict[str, str] = {
            'base_templates': 'template',
            'base_sm_comps': 'tdComp'
        }

        collections: list = []
        contents: list = []

        op_sources: list[str] = ['base_tools']
        source_exclude_list: list[str] = ['base_template', 'base_icon']
        set_exclude_list: list[str] = ['base_icon',]
        all_ops: list = []

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
                    contents.append(info)

                    all_ops.append(each_block)

                    # handle each example itself
                    for each_example in single_examples:
                        # skip template and icon ops
                        if each_example.name in source_exclude_list:
                            pass
                        else:
                            print(f'---> {each_example.name}')
                            path: str = f"{each_block.par.Blockname.eval()}/{each_example.par.Compname.eval()}"
                            info: dict = self._generate_op_info(
                                each_example, path)
                            contents.append(info)

        print('-> completing build')

        collections.append({'author': 'SudoMagic', 'contents': contents})
        inventory['collections'] = collections
        self.write_inventory_to_file(inventory)

    def _generate_op_info(self, target_op: callable, path: str) -> dict:

        # generate all the info needed for dict
        asset_path: str = None
        summary: str = None
        type_tag: str = 'block' if 'block' in target_op.tags else 'template'
        display_name: str = target_op.par.Blockname.eval(
        ) if 'block' in target_op.tags else target_op.par.Compname.eval()
        tox_version: str = None if 'block' in target_op.tags else target_op.par.Toxversion.eval()
        last_updated: str = None if 'block' in target_op.tags else target_op.par.Lastsaved.eval()
        td_version: str = None if 'block' in target_op.tags else f'{target_op.par.Tdversion.eval()}.{target_op.par.Tdbuild.eval()}'
        op_families: list = None
        op_types: list = None

        # write op to disk and generate path
        if 'block' in target_op.tags:
            summary = target_op.par.Summarycontents.eval().text
        else:
            children_ops = target_op.findChildren()
            asset_path = self.save_external(target_op)
            op_families = list(
                set([each_op.family for each_op in children_ops]))
            op_types = list(set([each_op.OPType for each_op in children_ops]))

        info: dict = {
            "path": path,
            "summary": summary,
            'type': type_tag,
            'display_name': display_name,
            'tox_version': tox_version,
            'last_updated': last_updated,
            'td_version': td_version,
            'asset_path': asset_path,
            'opFamilies': op_families,
            'opTypes': op_types,
        }

        return info

    def write_inventory_to_file(self, inventory: dict) -> None:

        print('--> writing inventory to file')
        with open(f'{self.release_dir_root}inventory.json', 'w+') as file:
            file.write(json.dumps(inventory))

    def save_external(self, target_op: callable) -> str:
        asset_path = f'{target_op.id}.{target_op.name}.tox'
        save_path = f'{self.release_dir_root}{asset_path}'
        target_op.save(save_path)
        return asset_path
