// KvEditor.tsx
import React, {useState} from 'react';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import ClearIcon from '@mui/icons-material/Clear';
import {Box, Card, Divider} from "@mui/material";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";

type KV = { name: string; value: string };

interface KvEditorProps {
    kvs: KV[];
    onChange: (updatedKVs: KV[]) => void;
}

export function KvEditor() {
    const [kvs, setKvs] = useState<KV[]>([]);
    const [newName, setNewName] = useState('');
    const [newValue, setNewValue] = useState('');

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

    const handleRemove = (index: number) => {
        const updatedKVs = kvs.filter((_, i) => i !== index);
        setKvs(updatedKVs);
    };

    const handleValueUpdate = (index: number, newValue: string) => {
        const updatedKVs = [...kvs];
        updatedKVs[index].value = newValue;
        setKvs(updatedKVs);
    };

    return (
        <Box>
            {kvs.map((kv, index) => (
                <Card

                    key={index}
                    sx={{display: 'flex', flexDirection: 'row', m: 2, p: 2}}
                >
                    <IconButton
                        sx={{borderRadius: 0}}
                        onClick={() => handleRemove(index)} aria-label="delete">
                        <ClearIcon/>
                    </IconButton>

                    <Box
                        sx={{display: 'flex', flexDirection: 'column', width: '100%'}}
                    >
                        <Typography sx={{mb: 2}}>
                            Argument: {kv.name}
                        </Typography>
                        <TextField
                            // label="Value"
                            value={kv.value}
                            onChange={(e) => handleValueUpdate(index, e.target.value)}
                            variant={'outlined'}
                        />
                    </Box>
                </Card>
            ))}

            <Divider>-</Divider>

            <Box
                sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    p: 2
                }}
            >
                <TextField
                    variant={'standard'}
                    label="New Argument"
                    value={newName}
                    onChange={handleNameChange}
                />
                <TextField
                    label="New Value"
                    variant={'standard'}
                    value={newValue}
                    onChange={handleValueChange}
                />
                <Button
                    onClick={handleAdd}
                    disabled={!newName || !newValue}
                >Add</Button>
            </Box>

        </Box>
    );
};

