import React from "react";
import {useNavigate, useParams, useSearchParams, Link as RouterLink} from "react-router-dom";
import {Features, useAppContext} from "../features";
import {Alert, Box, Button, Chip, IconButton, LinearProgress} from "@mui/material";
import {useMutation} from "@tanstack/react-query";
import {KvEditor} from "../components/KvEditor";
import {TextEditor} from "../components/TextEditor";
import {CopyableOutput} from "../components/CopyableOutput";
import FunctionsIcon from '@mui/icons-material/Functions';
import Typography from "@mui/material/Typography";
import KeyboardReturnIcon from '@mui/icons-material/KeyboardReturn';
import LambdaIcon from "../components/LambdaIcon";

export function FunctionViewPage(props: {}) {
    const param = useParams();
    const navigate = useNavigate();
    let [searchParams, setSearchParams] = useSearchParams();
    const fnName = searchParams.get('name');
    const appCtx = useAppContext();
    const fn = appCtx.status.fns.find(fn => fn.name === fnName)
    const submitMutation = useMutation({
        mutationFn: (value: any) => {
            return Features.inference(fnName!, value)
        },
    })
    const allowNullary = fn?.definition.mode.includes('no_arg');
    const isKeyWord = fn?.definition.mode.includes('keyword');
    const isUnary = fn?.definition.mode.includes('pos');

    let editor;
    if (isKeyWord) {
        editor = <KvEditor
            requiredKeywords={fn?.definition.required_args}
            onSubmit={submitMutation.mutate}
            allowNullary={allowNullary}/>
    } else if (isUnary) {
        editor = <TextEditor
            onSubmit={submitMutation.mutate}
            allowNullary={allowNullary}/>
    } else {
        editor = <Box>
            <Typography>This function requires no arguments</Typography>
            <Button onClick={() => {
                submitMutation.mutate(null)
            }}>Run</Button>
        </Box>
    }

    return <Box sx={{display: 'flex', flexDirection: 'column'}}>

        <Box sx={{ml: 4, display: 'flex', flexDirection: 'row', alignItems: 'center'}}>
            <IconButton
                color={'error'}
                component={RouterLink}
                to={'/'}
            ><KeyboardReturnIcon/></IconButton>
            <Box sx={{m: 1}}>
                <LambdaIcon/>
            </Box>
            <Typography>{fnName}</Typography>
        </Box>

        <Box>
            {editor}
        </Box>
        <Box sx={{mt: 2, mx: 4}}>
            {submitMutation.isError && <Alert severity="error">Something is wrong.</Alert>}
            {submitMutation.isLoading && <LinearProgress color="secondary"/>}
            {submitMutation.isSuccess && <CopyableOutput value={submitMutation.data.value}/>}
        </Box>

    </Box>
}

