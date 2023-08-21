import {TextareaAutosize} from "@mui/material";

export type InputType = 'json' | 'str'

export function InputEditor(
    {
        value, setValue, type
    }: {
        value: any, setValue: (nv: any) => void, type: InputType
    }) {
    return <>
        <TextareaAutosize value={value} onChange={e => setValue(e.target.value)}/>
    </>
}