import {Box, Card, Chip, Typography} from "@mui/material"
import React from "react"
import _ from "lodash"
import CodeBlock from '@theme/CodeBlock';
import {purple, red, orange, grey, green, blue, yellow} from '@mui/material/colors';

type Role = 'system' | 'user' | 'assistant' | 'function'
type Message = {
    role: Role
    content: string
    name?: string
}

type Example = {
    input: string | Record<string, string> | null
    output
}

type TextFunctionMode = 'kw' | 'pos' | 'no_args'
type TextFnTemplateType = {
    name?: string
    description?: string
    mode: TextFunctionMode[]
    examples: Example[]

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
                return <TextFnTemplateView template={template} name={name} module_name={module_name} key={name}/>
            })
        }
    </Box>
}

export function ExeModeBadge({
                                 mode
                             }: { mode: TextFunctionMode }) {
    switch (mode) {
        case "kw":
            return <Chip label={'Keyword'} sx={{bgcolor: purple[50]}}/>
        case "pos":
            return <Chip label={'Positional'} sx={{bgcolor: red[50]}}/>
        case "no_args":
            return <Chip label={'Nullary'} sx={{bgcolor: orange[50]}}/>
    }
    return <Chip label={mode}/>
}

function exampleInputToPyStr(input: string | Record<string, string> | null) {
    if (input === null || input === undefined) {
        return ''
    } else if (typeof input === 'string' || input instanceof String) {
        return JSON.stringify(input);
    } else {
        const keyValuePairs = Object.entries(input)
            .map(([key, value]) => `  ${key}=${JSON.stringify(value)}`)
            .join(', \n');
        return `\n${keyValuePairs}\n`;
    }
}

function formatOutputAsPyComment(output: string) {
    const lines = output.split("\n");
    return "# Output:\n" + _.join(
        lines.map((line, idx) => {
            // if (idx === 0) {
            //     return `# ${line}`
            // }
            return `#   ${line}`
        }), "\n");

}

export function TextFnTemplateView({
                                       template, module_name, name
                                   }: {
    template: TextFnTemplateType, module_name: string, name: string
}) {
    const importExample = `from ${module_name} import ${name}\n`
    const codeExample = template.examples.map(example => {
        return `${name}(${exampleInputToPyStr(example.input)})\n${formatOutputAsPyComment(example.output)}`
    }).join("\n")

    return <Box>
        <Box sx={{bgcolor: grey[50]}}>
            {template.description && <Typography>{template.description}</Typography>}
        </Box>
        <CodeBlock title={'Usage'} language="py">
            {importExample}
            {codeExample}
        </CodeBlock>
        <Box sx={{py: 2}}>
            <Typography
                sx={{mb: 1}}
                fontWeight={'bold'}
            >Execution Mode: </Typography>
            {template.mode.map(mode => {
                return <ExeModeBadge key={mode} mode={mode}/>
            })}
        </Box>
        {template.default_message && <CodeBlock title={'Default Message'}>{template.default_message}</CodeBlock>}
        {template.message_template && <CodeBlock title={'Message Template'}>{template.message_template}</CodeBlock>}
        <Box>

            <Typography
                sx={{mb: 1}}
                fontWeight={'bold'}
            >Init Messages: </Typography>
            <Box sx={{ml: 4}}>
                {template.init_messages.map(msg => {
                    return <MessageView {...msg} />
                })}
            </Box>

        </Box>

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

    let messageTypeBadge;
    let bgColor;
    let badgeDirection: 'left' | 'right' = 'left';
    switch (messageType) {
        case "System":
            bgColor = grey[100]
            messageTypeBadge = <Chip label={'System'} sx={{bgcolor: bgColor, borderRadius: 1}}/>
            break;
        case "User":
            badgeDirection = 'right'
            bgColor = green[200]
            messageTypeBadge = <Chip label={"User"} sx={{bgcolor: bgColor, borderRadius: 1}}/>
            break;
        case "Assistant":
            bgColor = blue[200]
            messageTypeBadge = <Chip label={"Assistant"} sx={{bgcolor: bgColor, borderRadius: 1}}/>

            break;
        case "Function":
            bgColor = yellow[200]
            messageTypeBadge = <Chip label={"Function"} sx={{bgcolor: bgColor, borderRadius: 1}}/>

            break;
        case "ExampleUser":
            badgeDirection = 'right'
            bgColor = green[50]
            messageTypeBadge = <Chip label={"ExampleUser"} sx={{bgcolor: bgColor, borderRadius: 1}}/>

            break;
        case "ExampleAssistant":
            bgColor = blue[50]
            messageTypeBadge = <Chip label={"ExampleAssistant"} sx={{bgcolor: bgColor, borderRadius: 1}}/>

            break;
    }

    return <Box sx={{
        borderRadius: 3,
        borderColor: grey[200],
        borderWidth: '1px',
        borderStyle: 'solid',
        px: 2, py: 1, mb: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: badgeDirection === 'left' ? 'flex-start' : 'flex-end',
    }}>
        <Box sx={{
            mb: 1,
            display: 'flex',
            flexDirection: badgeDirection === 'left' ? 'row' : 'row-reverse',
            justifyContent: messageType === 'System' ? 'center' : undefined
        }}>

            {messageTypeBadge}
        </Box>
        <Box sx={{
            bgcolor: bgColor,
            p: 1,
            borderRadius: 1,
            maxWidth: '80%',
            textAlign: 'left',
            whiteSpace: 'pre-line;'
        }}>
            {content}
        </Box>
    </Box>
}