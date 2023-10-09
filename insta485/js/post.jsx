import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import Comment from "./comment";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import duration from "dayjs/plugin/duration";
import timezone from "dayjs/plugin/timezone";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */
  const [owner, setOwner] = useState("");
  const [imgUrl, setImgUrl] = useState("");
  const [ownerShowUrl, setOwnerShowUrl] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [created, setCreated] = useState("");
  const [postShowUrl, setPostShowUrl] = useState("");
  const [postid, setPostid] = useState(0);
  // for comment component
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState("");
  const [comments_url, setCommentUrl] = useState("");


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
          // humanize the created time          
          dayjs.extend(relativeTime);
          dayjs.extend(utc);
          dayjs.extend(duration);
          dayjs.extend(timezone);
          const curTime = dayjs.utc();
          const localCurTime = curTime.local();
          const localCreatedTime = dayjs(data.created).utc('z').local().tz('America/Detroit');
          const timeDiff = localCreatedTime.diff(localCurTime);
          const humanizedTime = dayjs.duration(timeDiff).humanize(true);

          setComments([...data.comments]);
          setOwner(data.owner);
          setOwnerShowUrl(data.ownerShowUrl);
          setImgUrl(data.imgUrl);
          setCreated(humanizedTime);
          setPostShowUrl(data.postShowUrl);
          setOwnerImgUrl(data.ownerImgUrl);
          setCommentUrl(data.comments_url);
          setPostid(data.postid);
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

  // get the handleTextChange event value and set the text to the value
  const handleTextChange = (e) => {
    setCommentText(e.target.value);
  };

  // send a POST request to create a new comment and update the comments state
  const handleCommentSubmit = async (e) => {
    // prevent the page from reloading
    e.preventDefault();
    // empty comment
    if (commentText.trim() === '') {
      return;
    }
    fetch(`${comments_url}`, 
      { credentials: "same-origin",
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: commentText }) })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setComments([...comments, data]);
        setCommentText('');
      })
      .catch((error) => console.log(error));
  };

  // send the DELETE request to the API based on the id passed from the button
  const handleDeleteButton = async (commentid) => {
    fetch(`/api/v1/comments/${commentid}/`,
      { credentials: "same-origin",
        method: "DELETE",
        headers: {
          'Content-Type': 'application/json',
        }})
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          // remove the comment from the comments state
          setComments(comments.filter((comment) => comment.commentid != commentid))
        })
        .catch((error) => console.log(error));
  };

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
          <Comment
            key = {postid}
            handleTextChange={handleTextChange}
            handleCommentSubmit = {handleCommentSubmit}
            handleDeleteButton={handleDeleteButton}
            commentText = {commentText}
            comments = {comments}
          />
      </div>
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};
