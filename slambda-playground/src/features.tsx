import axios from "axios";
import React from 'react';


type Role = 'system' | 'user' | 'assistant' | 'function'
type Message = {
    role: Role
    content: string
    name?: string
}

type Example = {
    input: string | Record<string, string> | null
    output: string | Record<string, string>
}

type FunctionInputType = 'keyword' | 'unary'

type InputConfig = {
    input_type: FunctionInputType
    allow_none: boolean
    strict_no_args: boolean
}

type OutputConfig = {
    cast_to_json: boolean
}

type TextFnTemplateType = {
    instruction: string
    examples: Example[]

    message_stack: Message[]

    input_config: InputConfig
    output_config: OutputConfig

    default_args?: string

    message_template?: string
    required_args?: string[]

    name?: string
    gpt_opts: {
        model?: string,
        temperature?: number
        n?: number
        top_p?: number
        stream?: boolean
        stop?: string | string[]
        max_tokens?: number
        presence_penalty?: number
        frequency_penalty?: number
        logit_bias?: Record<number, number>
        user?: string
    }
}

export type NamedDefinition = {
    name: string
    definition: TextFnTemplateType
}

export type ServerStatus = {
    has_key: boolean,
    fns: NamedDefinition[]
}

export type FnResult = {
    type: ValueType
    value: string | any
}

export type ValueType = 'json' | 'none' | 'string'

export type LogEntry = {
    entry_id: string
    fn_name: string
    input_type: ValueType
    output_type: ValueType
    input_data: any
    output_data: any
    ts: string
}

export const Features = {
    async getStatus() {
        return axios.get<ServerStatus>('/api/status')
    },

    async inference(name: string, input: string | any) {
        const resp = await axios.post<FnResult>('/api/inference', {name, input})
        return resp.data;
    },

    async listLogs(page: number) {
        return axios.get<{
            entries: LogEntry[]
        }>('/api/inference-log', {
            params: {
                page
            }
        })
    },

    async removeLog(logId: string) {
        return axios.delete(`/api/log/${logId}`)
    },
}

export type AppContextType = {
    status: ServerStatus,
    isReady: boolean,
}

const AppContext = React.createContext<AppContextType | null>(null)
const AppContextAction = React.createContext<{
    updateStatus: () => void
} | null>(null)

export function AppContextProvider({children}: any) {
    const [value, setValue] = React.useState<AppContextType>({
        isReady: false,
        status: {
            has_key: false,
            fns: []
        },
    });
    const updateStatus = async () => {
        const statusResp = await Features.getStatus();
        setValue({
            isReady: true,
            status: statusResp.data,
        })
    }
    return <AppContext.Provider value={value}>
        <AppContextAction.Provider value={{updateStatus}}>
            {children}
        </AppContextAction.Provider>
    </AppContext.Provider>
}

export function useAppContextAction() {
    const action = React.useContext(AppContextAction)
    if (action === null) {
        throw Error('You should call this function within AppContextAction.Provider')
    }
    return action;
}

export function useAppContext() {
    const ctx = React.useContext(AppContext)
    if (ctx === null) {
        throw Error('You should call this function within AppContext.Provider')
    }
    return ctx;
}