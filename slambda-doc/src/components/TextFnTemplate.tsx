import { Box, Card } from "@mui/material"
import React from "react"
import _ from "lodash"
import CodeBlock from '@theme/CodeBlock';

type Role = 'system' | 'user' | 'assistant' | 'function'
type Message = {
    role: Role
    content: string
    name?: string
}
type TextFunctionMode = 'kw' | 'pos' | 'no_args'
type TextFnTemplateType = {
    name?: string
    description?: string
    mode: TextFunctionMode[]

    init_messages: Message[]
    default_message?: string
    message_template?: string

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

type TextFnModuleType = {
    module_name: string,
    fns: TemplateAndFnName[]
}

type TemplateAndFnName = {
    name: string
    template: TextFnTemplateType
}

export function TextFnModuleView({
    fns, module_name
}: TextFnModuleType) {
    return <Box>
        {
            _.map(fns, ({template, name}) => {
                return <TextFnTemplateView template={template} name={name} module_name={module_name} key={name} />
            })
        }
    </Box>
}



export function TextFnTemplateView({
    template, module_name, name
}: {
    template: TextFnTemplateType, module_name: string, name: string
}) {
    return <Box>
        <CodeBlock title={'Usage'} language="py">{`from ${module_name} import ${name}`}</CodeBlock>
        {template.default_message && <CodeBlock title={'Default Message'}>{template.default_message}</CodeBlock>}
        {template.message_template && <CodeBlock title={'Message Template'}>{template.message_template}</CodeBlock>}
        
    </Box>
}


type MessageType = 'System'
    | 'User'
    | 'Assistant'
    | 'Function'
    | 'ExampleUser'
    | 'ExampleAssistant'



export function MessageView({
    role,
    content,
    name
}: Message) {

    let messageType: MessageType
    if (role === 'system') {
        if (name === 'example_user') {
            messageType = "ExampleUser"
        } else if (name === 'example_assistant') {
            messageType = "ExampleAssistant"
        } else {
            messageType = "System"
        }
    } else if (role === 'user') {
        messageType = "User"
    } else if (role === 'assistant') {
        messageType = "Assistant"
    } else if (role === 'function') {
        messageType = "Function"
    }

    return <Card>
        {content}
    </Card>
}