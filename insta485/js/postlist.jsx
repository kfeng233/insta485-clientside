import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import Post from "./post";

export default function PostList({ url }) {
    const [ListPost, setListPost] = useState([]);
    useEffect(() => {
        // Declare a boolean flag that we can use to cancel the API request.
        let ignoreStaleRequest = false;
    
        // Call REST API to get the post's information
        fetch(url, { credentials: "same-origin" })
          .then((response) => {
            if (!response.ok) throw Error(response.statusText);
            return response.json();
          })
          .then((data) => {
            // If ignoreStaleRequest was set to true, we want to ignore the results of the
            // the request. Otherwise, update the state to trigger a new render.
            if (!ignoreStaleRequest) {
              setListPost(data.results);
            }
          })
          .catch((error) => console.log(error));
        //console.log("hello")
        return () => {
          // This is a cleanup function that runs whenever the Post component
          // unmounts or re-renders. If a Post is about to unmount or re-render, we
          // should avoid updating state.
          ignoreStaleRequest = true;
        };
    }, [url]);
    return (
        <ul>{ListPost?.map(item => <Post key = {item.postid} url={item.url}/>)}</ul>
    );
}

PostList.propTypes = {
    url: PropTypes.string.isRequired,
  };