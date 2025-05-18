import json

base_uri: str = "https://sudo-tools-td-templates.sudo.codes/builds/"


def build_inventory():
    print('-> Starting build process')

    inventory = {
        "setup": {
            "base_uri": base_uri
        },
    }

    name_to_type_map = {
        'base_templates': 'template',
        'base_sm_comps': 'tdComp'
    }

    collections = []
    contents = []

    op_sources = ['base_templates', 'base_sm_comps']
    source_exclude_list = ['base_template', 'base_icon']
    set_exclude_list = ['base_icon',]
    all_ops = []

    for each_source in op_sources:
        block_ops = op(each_source).findChildren(type=baseCOMP, depth=1)

        for each_block in block_ops:
            if each_block.name in source_exclude_list:
                pass
            else:
                print(f'--> {each_block.name}')
                external_ops = each_block.findChildren(type=baseCOMP, depth=1)
                assets = []
                set_info = {
                    'block': each_block.par.Blockname.eval(),
                    'summary': op(each_block.par.Summarycontents.eval()).text,
                    'type': name_to_type_map.get(each_source)
                }

                for each_external_op in external_ops:
                    if each_external_op.name in set_exclude_list:
                        pass
                    else:
                        # save op
                        asset_path = save_external_tox(each_external_op)

                        external_op_contents = each_external_op.findChildren()

                        opFamilies = [
                            op_content.family for op_content in external_op_contents]
                        opTypes = [
                            op_content.OPType for op_content in external_op_contents]

                        # build dict of child info
                        child_info = {
                            'display_name': each_external_op.par.Compname.eval(),
                            'type': name_to_type_map.get(each_source),
                            'tox_version': each_external_op.par.Toxversion.eval(),
                            'last_updated': each_external_op.par.Lastsaved.eval(),
                            'td_version': f'{each_external_op.par.Tdversion.eval()}.{each_external_op.par.Tdbuild.eval()}',
                            'asset_path': asset_path,
                            'opFamilies': list(set(opFamilies)),
                            'opTypes': list(set(opTypes)),
                        }
                        assets.append(child_info)
                        print('----> building info dict')

                set_info['assets'] = assets
                contents.append(set_info)

    collections.append({'author': 'SudoMagic', 'contents': contents})

    inventory['collections'] = collections

    print('--> writing inventory to file')
    with open('release/builds/latest/inventory.json', 'w+') as file:
        file.write(json.dumps(inventory))

    print('-> completing build')


def save_external_tox(target_op: callable) -> str:
    asset_path = f'tox/{target_op.id}.{target_op.name}.tox'
    save_path = f'release/builds/latest/{asset_path}'
    target_op.save(save_path)
    return asset_path
