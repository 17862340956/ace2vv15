#!/usr/bin/env python3
"""Verify DDK-built KO identity/CFI/callback DWARF; retain explicit OEM ABI gaps."""
from pathlib import Path
import json,sys,hashlib
from fix_vermagic import entries,field,TARGET,REVISION
from elftools.elf.elffile import ELFFile


def report(path):
    data=path.read_bytes();items=entries(data)
    if field(items,b'name')!=b'cpuinfo_spoof' or field(items,b'version')!=REVISION:
        raise ValueError('wrong module name/revision')
    vm=field(items,b'vermagic').decode()
    if vm.split()[0]!=TARGET.decode():raise ValueError('target vermagic mismatch')
    basis=field(items,b'source_basis').decode();commit=field(items,b'source_commit').decode()
    if basis!='PHP110_901_EXPERIMENTAL' or commit!='cd19560616750906a568aa271d8b49ac17f13914':
        raise ValueError('source metadata mismatch')
    callbacks={}
    expected={'fake_available':['cpufreq_policy *','char *'],
              'fake_topology':['device *','device_attribute *','char *'],
              'fake_cpu_mask':['device *','device_attribute *','char *'],
              'fake_cpuinfo_open':['inode *','file *'],
              'fake_cpuinfo_show':['seq_file *','void *']}
    with path.open('rb') as f:
        elf=ELFFile(f)
        if not elf.has_dwarf_info():raise ValueError('unstripped callback DWARF required')
        def typename(d):
            if d is None:return 'void'
            if d.tag in ('DW_TAG_typedef','DW_TAG_const_type','DW_TAG_volatile_type'):
                return typename(d.get_DIE_from_attribute('DW_AT_type'))
            if d.tag=='DW_TAG_pointer_type':
                return typename(d.get_DIE_from_attribute('DW_AT_type') if 'DW_AT_type' in d.attributes else None)+' *'
            n=d.attributes.get('DW_AT_name');return n.value.decode() if n else d.tag
        for cu in elf.get_dwarf_info().iter_CUs():
            for d in cu.iter_DIEs():
                n=d.attributes.get('DW_AT_name')
                if d.tag!='DW_TAG_subprogram' or not n:continue
                name=n.value.decode(errors='replace')
                if name not in expected:continue
                params=[c for c in d.iter_children() if c.tag=='DW_TAG_formal_parameter']
                if not params or any('DW_AT_type' not in c.attributes for c in params):continue
                args=[typename(c.get_DIE_from_attribute('DW_AT_type')) for c in params]
                if args!=expected[name]:raise ValueError('callback mismatch '+name+': '+str(args))
                callbacks[name]=args
        if set(callbacks)!=set(expected):raise ValueError('missing callback DWARF')
        symtab=elf.get_section_by_name('.symtab')
        names=[s.name for s in symtab.iter_symbols()] if symtab else []
        if not any(n=='__cfi_check' or n.startswith('__cfi_check.') for n in names):raise ValueError('CFI check missing')
        ver=elf.get_section_by_name('__versions')
        version_bytes=ver['sh_size'] if ver else 0
    return {'file':path.name,'revision':REVISION.decode(),'sha256':hashlib.sha256(data).hexdigest(),
            'size':len(data),'vermagic':vm,'source_basis':basis,'source_commit':commit,
            'build_mode':'DDK android12-5.10 with bundled901 private declarations',
            'callbacks':callbacks,'dwarf':'passed','cfi':'present','module_version_section_bytes':version_bytes,
            'target_1301_full_crc_proof':False,'private_layout_1301_verified':False,
            'runtime':'not tested','abi_limit':'DDK public layout/CRC plus901 private declarations are experimental; not OEM1301 ABI proof'}


if __name__=='__main__':
    try:
        p=Path(sys.argv[1]);r=report(p)
        Path(sys.argv[2]).write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode())
        print(json.dumps(r,ensure_ascii=False,indent=2))
    except Exception as e:raise SystemExit('KO verification failed: '+str(e))
