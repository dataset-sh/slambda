// KvEditor.tsx
import React, {useState} from 'react';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import ClearIcon from '@mui/icons-material/Clear';
import {Box, Card, Chip, Divider, InputLabel, TextareaAutosize} from "@mui/material";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import UploadRoundedIcon from "@mui/icons-material/UploadRounded";
import {blue, blueGrey, grey, lightGreen, teal} from '@mui/material/colors';
import {styled} from "@mui/system";
import AddIcon from '@mui/icons-material/Add';
import EqualIcon from "./EqualIcon";
import _ from 'lodash';
import SouthIcon from '@mui/icons-material/South';
import NorthIcon from '@mui/icons-material/North';


type KV = { name: string; value: string };


const StyledTextarea = styled(TextareaAutosize)(
    ({theme}) => `
    font-family: IBM Plex Sans, sans-serif;
    font-size: 0.875rem;
    font-weight: 400;
    line-height: 1.5;
    padding: 12px;
    border-radius: 6px 6px 6px 6px;
    color: ${theme.palette.mode === 'dark' ? grey[300] : grey[900]};
    background: ${theme.palette.mode === 'dark' ? grey[900] : grey[100]};
    border: 2px solid ${theme.palette.mode === 'dark' ? grey[700] : grey[500]};
    box-shadow: 0px 2px 2px ${theme.palette.mode === 'dark' ? grey[900] : grey[50]};
  
    &:hover {
      border-color: ${blue[400]};
    }
  
    &:focus {
      border-color: ${blue[400]};
      box-shadow: 0 0 0 3px ${theme.palette.mode === 'dark' ? blue[500] : blue[200]};
    }
  
    // firefox
    &:focus-visible {
      outline: 0;
    }
  `,
);

const SmallStyledTextarea = styled(TextareaAutosize)(
    ({theme}) => `
    font-family: IBM Plex Sans, sans-serif;
    font-size: 0.875rem;
    font-weight: 400;
    line-height: 1;
    padding: 12px;
    border-radius: 6px 6px 6px 6px;
    color: ${theme.palette.mode === 'dark' ? grey[300] : grey[900]};
    background: ${theme.palette.mode === 'dark' ? grey[900] : grey[100]};
    border: 2px solid ${theme.palette.mode === 'dark' ? grey[700] : grey[500]};
    box-shadow: 0px 2px 2px ${theme.palette.mode === 'dark' ? grey[900] : grey[50]};
  
    &:hover {
      border-color: ${blue[400]};
    }
  
    &:focus {
      border-color: ${blue[400]};
      box-shadow: 0 0 0 3px ${theme.palette.mode === 'dark' ? blue[500] : blue[200]};
    }
  
    // firefox
    &:focus-visible {
      outline: 0;
    }
  `,
);


function FixedKeywordEditor(
    {kv, onChange, onRemove}: {
        kv: KV,
        onChange: (value: string) => void,
        onRemove?: () => void,
    }) {
    return <Box sx={{width: '100%', my: 1}}>
        <Box sx={{display: 'flex', flexDirection: 'row', alignItems: 'center'}}>
            <TextField
                size={'small'}
                variant={'outlined'}
                label="Argument Name"
                defaultValue={kv.name}
                InputProps={{
                    readOnly: true,
                }}
            />

            <Box sx={{mx: 1}}><EqualIcon/></Box>

            <TextField
                size={'small'}
                fullWidth
                value={kv.value}
                onChange={(e) => onChange(e.target.value)}
            />


            {onRemove ? <IconButton
                color={'error'}
                // size={'small'}
                sx={{mr: 1}}
                onClick={onRemove} aria-label="delete">
                <ClearIcon/>
            </IconButton> : null}
        </Box>
    </Box>
}

export function KvEditor(
    {
        allowNullary,
        requiredKeywords,
        onSubmit
    }: {
        allowNullary: boolean,
        onSubmit: (kv: any) => void,
        requiredKeywords?: string[]
    }) {
    const [kvs, setKvs] = useState<KV[]>([]);
    const [newName, setNewName] = useState('');
    const [newValue, setNewValue] = useState('');
    const [expanded, setExpanded] = React.useState(false);

    const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setNewName(event.target.value);
    };

    const handleValueChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setNewValue(event.target.value);
    };

    const handleAdd = () => {
        if (newName && newValue) {
            const newKV: KV = {name: newName, value: newValue};
            setKvs([...kvs, newKV]);
            setNewName('');
            setNewValue('');
        }
    };

    const handleRemove = (name: string) => {
        const updatedKVs = kvs.filter((kv) => kv.name !== name);
        setKvs(updatedKVs);
    };

    const handleValueUpdate = (name: string, newValue: string) => {
        const updatedKVs = [];
        let found = false;
        for (const kv of kvs) {
            if (kv.name === name) {
                updatedKVs.push({name, value: newValue})
                found = true;
            } else {
                updatedKVs.push(kv)
            }

        }
        if (!found) {
            updatedKVs.push({name, value: newValue})
        }

        setKvs(updatedKVs);
    };

    return (
        <Box sx={{
            backgroundColor: grey[50],
            px: 2,
            py: 2,
            borderRadius: 2,
        }}>

            {requiredKeywords && requiredKeywords.map((requiredKey) => (
                <Box
                    key={requiredKey}
                    sx={{display: 'flex', flexDirection: 'row'}}
                >
                    <FixedKeywordEditor kv={{
                        name: requiredKey,
                        value: kvs.find(kv => kv.name === requiredKey)?.value || ''
                    }} onChange={(newValue) => {
                        handleValueUpdate(requiredKey, newValue)
                    }}/>
                </Box>
            ))}


            {kvs.filter(kv => !requiredKeywords?.includes(kv.name)).map((kv) => (
                <Box
                    key={kv.name}
                    sx={{display: 'flex', flexDirection: 'row'}}
                >
                    <FixedKeywordEditor
                        onRemove={() => {
                            handleRemove(kv.name)
                        }}
                        kv={kv} onChange={(newValue) => {
                        handleValueUpdate(kv.name, newValue)
                    }}/>
                </Box>
            ))}

            <Divider sx={{mb: 1}}>λ</Divider>

            <Box>
                <Button
                    fullWidth
                    sx={{justifyContent: 'flex-start', mb: 1}}
                    onClick={() => setExpanded(!expanded)}
                    endIcon={expanded ? <NorthIcon/> : <SouthIcon/>}
                    // startIcon={expanded ? <NorthIcon/> : <SouthIcon/>}
                >
                    New Keyword Argument
                </Button>

                {expanded && <Box>

                    <Box sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        // px: 1
                    }}>
                        <Box sx={{
                            display: 'flex',
                            flexDirection: 'row',
                            alignItems: 'center'
                        }}>
                            <TextField
                                sx={{width: '15rem', mb: 1}}
                                size={'small'}
                                variant={'outlined'}
                                value={newName}
                                label={'Argument Name'}
                                onChange={handleNameChange}
                            />


                            <Box
                                sx={{mx: 1}}
                            ><EqualIcon/></Box>


                            <TextField
                                sx={{mb: 1}}
                                size={'small'}
                                fullWidth
                                multiline
                                variant={'outlined'}
                                value={newValue}
                                label={'Argument Value'}
                                onChange={e => setNewValue(e.target.value)}
                            />
                        </Box>


                    </Box>

                    <Box
                        sx={{display: 'flex', flexDirection: 'row', alignItems: 'center'}}
                    >
                        <Box
                            sx={{flexGrow: 1}}
                        >
                            <Button
                                color={'success'}
                                variant={'outlined'}
                                onClick={handleAdd}
                                disabled={!newName || !newValue}
                                startIcon={<AddIcon/>}
                            >
                                {newName ? `Add keyword: ${newName}` : 'Add'}
                            </Button
                            >
                        </Box>

                        <IconButton
                            color={'error'}
                            // size={'small'}
                            sx={{mr: 1}}
                            onClick={() => {
                                setNewName('')
                                setNewValue('')
                            }} aria-label="delete">
                            <ClearIcon/>
                        </IconButton>

                    </Box>

                </Box>}


            </Box>

            <Divider sx={{my: 2}}></Divider>

            <Button
                onClick={() => onSubmit(combineKVs(kvs))}
                color={'success'}
                variant={'contained'}
                sx={{color: grey[200]}}
                disabled={!canSubmit(kvs, allowNullary, requiredKeywords)}
                endIcon={<UploadRoundedIcon/>}
            >Submit</Button>
        </Box>
    );
};


function combineKVs(kvs: KV[]){
    const ret: any = {}
    for (let kv of kvs){
        ret[kv.name] = kv.value;
    }
    return ret;
}

function canSubmit(kvs: KV[], allowNullary: boolean, required?: string[]) {
    if (!required) {
        required = [];
    }
    const hasAllRequired = _.every(
        required,
        name => _.some(kvs, kv => kv.name === name && kv.value)
    )
    if (hasAllRequired) {
        return allowNullary || (kvs && kvs.length > 0);
    } else {
        return false;
    }
}
