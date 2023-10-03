import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */
  
  const [comments, setComments] = useState([]);
  const [owner, setOwner] = useState("");
  const [imgUrl, setImgUrl] = useState("");
  const [ownerShowUrl, setOwnerShowUrl] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [created, setCreated] = useState("");
  const [postShowUrl, setPostShowUrl] = useState("");
  const [commentUrl, setCommentUrl] = useState("");

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
          console.log(data)
          setComments([...data.comments]);
          setOwner(data.owner);
          setOwnerShowUrl(data.ownerShowUrl);
          setImgUrl(data.imgUrl);
          setCreated(data.created);
          setPostShowUrl(data.postShowUrl);
          setOwnerImgUrl(data.ownerImgUrl);
          setCommentUrl(data.commentUrl);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  // Render post image and post owner
  return (
    <div className="posts">
      <div>
        <a href={ownerShowUrl}>
          <img src={ownerImgUrl} alt="owner_profile" className="profiles"/>
          {owner}
        </a>
        <a href={postShowUrl} className="created">{created}</a>
      </div>
      <img src={imgUrl} alt="post_image" className="post_img"/>
      <div>
        {comments?.map((comment) =>
          <div key = {comment.commentid}>
            <a href={comment.ownerShowUrl}>{comment.owner}: </a>
            {comment.text}
          </div>
        )}
      </div>
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
  //owner: PropTypes.string.isRequired
};
