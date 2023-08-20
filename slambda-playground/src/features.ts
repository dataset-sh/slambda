import axios from "axios";

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

export const Features = {
    getStatus() {
        return axios.get<ServerStatus>('/api/status')
    },

    inference(input: string | any) {
        return axios.post('/api/inference', {})
    },
}