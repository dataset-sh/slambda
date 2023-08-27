import {Box, Button, Divider, TextField} from "@mui/material";
import React from "react";
import Typography from "@mui/material/Typography";
import {grey} from "@mui/material/colors";

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

export function CopyableOutput({value, title}: { value: string, title?: string }) {
    const [copiedValue, copy] = useCopyToClipboard()
    const [copiedGuard, setCopiedGuard] = React.useState(false);

    return (
        <Box sx={{
            backgroundColor: grey[50],
            borderRadius: 2,
            borderWidth: '1px',
            borderColor: grey[300],
            borderStyle: 'solid',
        }}>
            <Box
                sx={{
                    backgroundColor: grey[200],
                    display: 'flex', flexDirection: 'row', alignItems: 'center', pl: 2
                }}
            >
                <Typography sx={{flexGrow: 1}}>
                    {title || 'Function Output'}
                </Typography>

                <Button onClick={() => {
                    setCopiedGuard(true)
                    copy(value)
                    setTimeout(() => {
                        setCopiedGuard(false)
                    }, 2500)
                }}>
                    <span>{(copiedValue && copiedGuard) ? 'Copied!' : 'Copy'}</span>
                </Button>
            </Box>
            <Divider/>
            <Box sx={{
                // mt: 2,
                p: 2,
            }}>
                <Typography
                    sx={{
                        whiteSpace: 'pre-wrap'
                    }}
                >
                    {value}
                </Typography>
            </Box>

        </Box>
    );
}
