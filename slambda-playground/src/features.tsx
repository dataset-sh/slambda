import axios from "axios";
import React from 'react';

export type NamedDefinition = {
    name: string
    definition: any
}

export type ServerStatus = {
    has_key: boolean,
    fns: NamedDefinition[]
}

export type FnResult = {
    value: string | any
}

export type ValueType = 'json' | 'none' | 'string'

export type LogEntry = {
    entry_id: string
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

    async inference(input: string | any) {
        return axios.post('/api/inference', {})
    },

    async listLogs(page: number) {
        return axios.get<{
            entries: LogEntry[]
        }>('/api/log', {
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