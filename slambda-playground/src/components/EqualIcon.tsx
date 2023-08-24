import * as React from 'react';
import SvgIcon from '@mui/material/SvgIcon';

export default function EqualIcon() {
    return (
        <SvgIcon>
            {/* credit: plus icon from https://heroicons.com/ */}
            <svg fill="#000000" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg"
                 width="800px" height="800px" viewBox="0 0 22.354 22.354"
            >
                <path
                    d="M5 9C4.44772 9 4 9.44771 4 10C4 10.5523 4.44772 11 5 11H19C19.5523 11 20 10.5523 20 10C20 9.44771 19.5523 9 19 9H5Z"
                    fill="#000000"
                />
                <path
                    d="M5 13C4.44772 13 4 13.4477 4 14C4 14.5523 4.44772 15 5 15H19C19.5523 15 20 14.5523 20 14C20 13.4477 19.5523 13 19 13H5Z"
                    fill="#000000"
                />
            </svg>
        </SvgIcon>
    );
}