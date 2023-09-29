import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import Post from "./post";

export default function PostList({ url }) {
    const[next, setNextUrl] = useState("")
    const[result, setResult] = useState("")

    useEffect(() => {
        let ignoreStaleRequest = false;
        fetch(url, { credentials: "same-origin" })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                if (!ignoreStaleRequest) {
                    console.log(data);
                    setNextUrl(data.next);
                    setResult(data.result);
                }
            })
            .catch((error) => console.log(error));
        
        return () => {
            ignoreStaleRequest = true;
        };
    }, [url]);

    return (
        <div></div>
    );
}

Post.propTypes = {
    url: PropTypes.string.isRequired,
};