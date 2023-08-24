import React from "react";
import {useNavigate, Link as RouteLink, useParams} from "react-router-dom";
import {Box, Button, TextareaAutosize} from "@mui/material";
import {grey, blue, teal} from '@mui/material/colors';
import {styled} from '@mui/system';
import Typography from "@mui/material/Typography";
import UploadRoundedIcon from '@mui/icons-material/UploadRounded';

const StyledTextarea = styled(TextareaAutosize)(
    ({theme}) => `
    font-family: IBM Plex Sans, sans-serif;
    font-size: 0.875rem;
    font-weight: 400;
    line-height: 1.5;
    padding: 12px;
    border-radius: 12px 12px 0 12px;
    color: ${theme.palette.mode === 'dark' ? grey[300] : grey[900]};
    background: ${theme.palette.mode === 'dark' ? grey[900] : grey[100]};
    border: 2px solid ${theme.palette.mode === 'dark' ? grey[700] : teal[500]};
    box-shadow: 0px 2px 2px ${theme.palette.mode === 'dark' ? grey[900] : teal[50]};
  
    &:hover {
      border-color: ${blue[400]};
    }
  
    &:focus {
      border-color: ${blue[400]};
      box-shadow: 0 0 0 3px ${theme.palette.mode === 'dark' ? blue[500] : blue[200]};
    }
  
    // firefox
    &:focus-visible {
      outline: 0;
    }
  `,
);


export function TextEditor({
                               allowNullary,
                               onSubmit
                           }: {
    allowNullary: boolean,
    onSubmit: (kv: any) => void
}) {
    const [value, setValue] = React.useState('');


    return <Box sx={{
        display: 'flex',
        flexDirection: 'column',
    }}>
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                // alignItems: 'center',
                // backgroundColor: '#EEF6FF',
                px: 4,
                mr: 4,
                mt: 1,
            }}
        >

            <Typography
                fontSize={'small'}
                fontWeight={'bold'}
                sx={{width: '100%', mb: 2}}>
                Input:
            </Typography>

            <StyledTextarea
                sx={{width: '100%'}}
                minRows={3}
                aria-label="function input"
                value={value} onChange={e => setValue(e.target.value)}/>
            <Box
                sx={{
                    display: 'flex',
                    flexDirection: 'row-reverse',
                    mt: 2,
                }}
            >
                <Button
                    onClick={() => {
                        onSubmit(value)
                    }}
                    color={'success'}
                    variant={'outlined'}
                    disabled={!allowNullary && !value}
                    endIcon={<UploadRoundedIcon/>}
                >Submit</Button>

            </Box>
        </Box>

    </Box>
}