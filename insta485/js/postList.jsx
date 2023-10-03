import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import Post from "./post";

export default function PostList({ url }) {
    const[posts, setPosts] = useState([])

    useEffect(() => {
        let ignoreStaleRequest = false;
        fetch(url, { credentials: "same-origin" })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                if (!ignoreStaleRequest) {
                    setPosts([...data.results])
                    // console.log(data)
                }
            })
            .catch((error) => console.log(error));
        
        return () => {
            ignoreStaleRequest = true;
        };
    }, [url]);
    return (
        <div>
            { posts?.map((post) =>
                <Post 
                    key={post.postid}
                    {...post}
                />
            )}
        </div>
    );
}

PostList.propTypes = {
    url: PropTypes.string.isRequired,
};