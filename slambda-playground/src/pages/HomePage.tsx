import React from "react";
import {useNavigate, Link as RouteLink, useParams} from "react-router-dom";
import {NamedDefinition, useAppContext} from "../features";
import {Box, Button, Card, CardActions, CardContent, Grid} from "@mui/material";
import Typography from "@mui/material/Typography";
import TextField from '@mui/material/TextField';
import {grey} from "@mui/material/colors";
import {
    Link as RouterLink,
} from 'react-router-dom';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import {Helmet} from "react-helmet-async";

export function FunctionNameView({name, definition}: NamedDefinition) {
    return <Card sx={{minHeight: '12em'}}>
        <CardContent sx={{height: '100%'}}>
            <Typography variant="h5" component="div" fontWeight={'bold'}>
                {name}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{mt: 1}}>
                {definition.description}
            </Typography>
        </CardContent>
        <CardActions>
            <Button
                color={'primary'}
                endIcon={<ArrowForwardIcon/>}
                component={RouterLink} to={`/playground?name=${name}`}
                sx={{ml: 1}} size="small">Run this function</Button>
        </CardActions>
    </Card>
}

export function HomePage(props: {}) {
    const param = useParams();
    const navigate = useNavigate();
    const appCtx = useAppContext();
    const [search, setSearch] = React.useState('')
    return <Box>
        <Helmet>
            <title>sλ Playground</title>
            <link rel="canonical" href="https://www.tacobell.com/"/>
        </Helmet>

        <Box sx={{
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',

        }}>
            <TextField
                label="Search"
                value={search}
                onChange={e => setSearch(e.target.value)}
                variant="outlined"
                size="small"
            />

            <Box
                component={'div'}
                sx={{
                    flexGrow: 1,
                }}></Box>

            <Typography>
                Total {appCtx.status.fns.length} functions
            </Typography>
        </Box>

        <Box
            sx={{
                p: 2,
                mt: 2,
                backgroundColor: grey[100],
                borderRadius: 2,
                flexGrow: 1,
                minHeight: '30vh',
            }}
        >
            <Grid
                container spacing={{xs: 2, md: 3}} columns={{xs: 1, md: 2}}>
                {appCtx.status.fns.filter(fn => fn.name.includes(search)).map(fn => {
                    return <Grid item xs={1} key={fn.name}>
                        <FunctionNameView key={fn.name} {...fn}/>
                    </Grid>
                })}

            </Grid>
        </Box>

    </Box>
}