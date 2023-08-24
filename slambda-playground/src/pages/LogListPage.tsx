import React from "react";
import {useNavigate, Link as RouteLink, useParams, useSearchParams} from "react-router-dom";
import {Helmet} from "react-helmet-async";
import {useQuery} from "@tanstack/react-query";
import {Features} from "../features";
import {Alert, Box, Card, LinearProgress} from "@mui/material";
import Typography from "@mui/material/Typography";
import {CopyableOutput} from "../components/CopyableOutput";
import moment from "moment";

export function LogListPage(props: {}) {
    const param = useParams();
    const navigate = useNavigate();
    let [searchParams, setSearchParams] = useSearchParams();
    const page = Number(searchParams.get('page') || '1')


    const info = useQuery({
            queryKey: ['logs', 'page', page],
            queryFn: async () => {
                return Features.listLogs(page)
            }
        }
    )

    return <>
        <Helmet>
            <title>sλ: logs</title>
            <link rel="canonical" href="https://www.tacobell.com/"/>
        </Helmet>

        <Box></Box>

        <Box>
            {info.isSuccess}
            {info.isLoading && <LinearProgress color="secondary"/>}
            {info.isError && <Alert severity="error">Something is wrong.</Alert>}
            {info.data?.data.entries.map((entry, i) => {
                const ts = moment(entry.ts)
                return <Card key={entry.entry_id} sx={{p: 2, mb: 4}}>
                    <Typography fontWeight={'bold'}>
                        {i + 1}. Function: {entry.fn_name}
                    </Typography>
                    <Typography fontSize={'small'} sx={{mb: 2}} fontWeight={'bold'}>
                        time: {ts.format('YYYY-MM-DD hh:mm:ss')} ({ts.fromNow()})
                    </Typography>
                    <Box sx={{mb: 2}}>
                        <CopyableOutput value={displayDataItem(entry.input_data)} title={'Function Input'}/>
                    </Box>

                    <CopyableOutput value={displayDataItem(entry.output_data)}/>
                </Card>
            })}
        </Box>
    </>
}

function displayDataItem(value?: Record<string, any> | string) {
    if (!value) {
        return "None"
    } else {
        if (typeof value === 'string' || value instanceof String) {
            return value.toString();
        } else {
            return JSON.stringify(value, null, 2)
        }
    }
}