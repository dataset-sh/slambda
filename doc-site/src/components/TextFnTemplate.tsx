import {Box, Card, Chip, Typography, Divider} from "@mui/material"
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

type GptParameters = {
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
                return <React.Fragment key={name}>
                    <TextFnTemplateView template={template} name={name} module_name={module_name}/>
                    <Divider sx={{mb: 6, mt: 8}}/>
                </React.Fragment>
            })
        }
    </Box>
}

export function InputConfigView({
                                    inputConfig
                                }: { inputConfig: InputConfig }) {

    if (inputConfig.allow_none && inputConfig.strict_no_args) {
        return <>
            <Typography component={'span'}>
                This function can only be called with
            </Typography> <Chip label={'NO ARGUMENTS'}/>
        </>
    } else {
        switch (inputConfig.input_type) {
            case "keyword":
                return <>
                    <Typography component={'span'}>
                        This function can be called with
                    </Typography> <Chip label={'KEYWORD ARGUMENTS'}/> {inputConfig.allow_none &&
                    <Chip label={'NO ARGUMENTS'}/>}
                </>
            case "unary":
                return <>
                    <Typography component={'span'}>
                        This function can be called with
                    </Typography> <Chip label={'POSITIONAL ARGUMENTS'}/> {inputConfig.allow_none &&
                    <Chip label={'NO ARGUMENTS'}/>}
                </>
        }
    }

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

function formatOutputAsPyComment(output: string | Record<string, any>) {
    if (!(typeof output === 'string')) {
        output = JSON.stringify(output)
    }
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
        <Box>
            <Typography variant="h4" sx={{mb: 2}}>
                Function: {name}
            </Typography>
        </Box>
        <Box sx={{bgcolor: grey[50]}}>
            {template.instruction && <Typography>{template.instruction}</Typography>}
        </Box>
        <CodeBlock title={'Usage'} language="py">
            {importExample}
            {codeExample}
        </CodeBlock>
        <Box sx={{py: 2}}>
            <Typography
                sx={{mb: 1}}
                fontWeight={'bold'}
            >Input Config: </Typography>
            <InputConfigView inputConfig={template.input_config}/>
            <Box>
                <Typography
                    sx={{mb: 1, mt: 1}}
                    fontWeight={'bold'}
                >Output Config: </Typography>
                <Typography
                    component={'span'}
                    sx={{mb: 1}}
                >Return format
                </Typography> {template.output_config.cast_to_json ? <Chip label={'JSON'}/> : <Chip label={'STRING'}/>}.
            </Box>
        </Box>
        {template.default_args && <CodeBlock title={'Default Message'}>{template.default_args}</CodeBlock>}
        {template.message_template && <CodeBlock title={'Message Template'}>{template.message_template}</CodeBlock>}
        <Box>

            <Typography
                sx={{mb: 1}}
                fontWeight={'bold'}
            >Message List: </Typography>
            <Box sx={{ml: 4}}>
                {template.message_stack.map(msg => {
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