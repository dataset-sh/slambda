import React from "react";
import {useNavigate, Link as RouteLink, useParams} from "react-router-dom";
import {useSearchParams} from "react-router-dom";
import Typography from "@mui/material/Typography";
import {Features, useAppContext} from "../features";
import {Alert, Box, Button, CircularProgress, LinearProgress, TextareaAutosize} from "@mui/material";
import {InputEditor} from "../components/InputEditor";
import TextField from "@mui/material/TextField";
import {useMutation, useQuery} from "@tanstack/react-query";
import FileCopyIcon from '@mui/icons-material/FileCopy';
import {KvEditor} from "../components/KvEditor";

function getInputType(definition: any) {
    const modes = definition.mode as string[]
    if (definition.mode.includes('keyword')) {

    }

    if (definition.mode.includes('pos')) {

    }

    if (definition.mode.includes('no_args')) {

    }
}

export function FunctionViewPage(props: {}) {
    const param = useParams();
    const navigate = useNavigate();
    let [searchParams, setSearchParams] = useSearchParams();
    const fnName = searchParams.get('name');
    const appCtx = useAppContext();
    const fn = appCtx.status.fns.find(fn => fn.name === fnName)
    const submitMutation = useMutation({
        mutationFn: (value: any) => {
            return Features.inference({
                name: fnName, input: value
            })
        },
    })

    return <>
        <Typography>
            {fnName}
        </Typography>

        {
            fn?.definition.mode.includes('keyword') && <KvEditor/>
        }

        {
            fn?.definition.mode.includes('pos') && <UnaryFunctionView/>
        }

        <Button>Submit</Button>
        {submitMutation.isError && <Alert severity="error">Something is wrong.</Alert>}
        {submitMutation.isLoading && <LinearProgress color="secondary"/>}
        {submitMutation.isSuccess && <Box>
            <CopyableOutput value={'hello world'}/>
        </Box>}
    </>
}


// type KV = { name: string, value: string }

// export function KeywordFunctionView() {
//     const [value, setValue] = React.useState<KV[]>([]);
//     const [kv, setKV] = React.useState<KV>({name: '', value: ''})
//     return <Box sx={{display: 'flex', flexDirection: 'column'}}>
//
//         {
//             value.map(kv => {
//                 return <Box key={kv.name}>
//                     <TextField label="Key Name" variant="standard"
//                                value={kv.name}/>
//                     <TextField label="Value" variant="standard"
//                                value={kv.value}/>
//                 </Box>
//             })
//         }
//
//         <Box sx={{display: 'flex', flexDirection: 'column'}}>
//             <TextField label="Key Name" variant="standard"/>
//             <TextField label="Value" variant="standard"/>
//             <Button>Add Keyword Argument</Button>
//         </Box>
//     </Box>
// }

export function UnaryFunctionView() {
    const [value, setValue] = React.useState('');
    return <Box>
        <TextareaAutosize value={value} onChange={e => setValue(e.target.value)}/>
    </Box>
}


type CopiedValue = string | null
type CopyFn = (text: string) => Promise<boolean> // Return success

export function useCopyToClipboard(): [CopiedValue, CopyFn] {
    const [copiedText, setCopiedText] = React.useState<CopiedValue>(null)

    const copy: CopyFn = async text => {
        if (!navigator?.clipboard) {
            console.warn('Clipboard not supported')
            return false
        }

        try {
            await navigator.clipboard.writeText(text)
            setCopiedText(text)
            return true
        } catch (error) {
            console.warn('Copy failed', error)
            setCopiedText(null)
            return false
        }
    }

    return [copiedText, copy]
}

function CopyableOutput({value}: { value: string }) {
    const [copiedValue, copy] = useCopyToClipboard()

    return (
        <Box>
            <Typography>{value}</Typography>
            <Button onClick={() => copy(value)}>
                <span>{copiedValue ? 'Copied!' : 'Copy'}</span>
            </Button>
        </Box>
    );
}
